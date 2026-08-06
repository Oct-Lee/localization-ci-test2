"""Gemini API client with retry, failover, and quota handling."""

from __future__ import annotations

import sys
import time
from typing import Any

import requests

from config import (
    DAILY_QUOTA_RE,
    GEMINI_MODELS,
    GEMINI_MODEL_QUOTAS,
    HTTP_TIMEOUT_SEC,
    MAX_ATTEMPTS,
    MAX_QUOTA_RETRIES,
    QUOTA_RETRY_DEFAULT_SEC,
    RESPONSE_SCHEMA,
    RETRY_IN_RE,
    GeminiModelQuota,
    gemini_endpoint,
    min_request_interval_sec,
)


class GeminiFailoverManager:
    """Sticky model index for quota/availability failover within one process."""

    def __init__(self, quotas: tuple[GeminiModelQuota, ...] = GEMINI_MODEL_QUOTAS) -> None:
        self._quotas = quotas
        self._index = 0

    def reset(self) -> None:
        self._index = 0

    def active_quota(self) -> GeminiModelQuota:
        return self._quotas[self._index]

    def active_model_id(self) -> str:
        return self.active_quota().model_id

    def try_advance(self, reason: str) -> bool:
        if self._index + 1 >= len(self._quotas):
            return False
        prev = self._quotas[self._index]
        self._index += 1
        nxt = self._quotas[self._index]
        print(
            f"Gemini model failover: {prev.model_id} -> {nxt.model_id} "
            f"(RPM={nxt.rpm}/RPD={nxt.rpd}; {reason})",
            file=sys.stderr,
        )
        return True

    def pace_after_failover(self) -> None:
        """Wait one full interval for the new model before the next request."""
        wait = min_request_interval_sec(self.active_quota().rpm)
        print(
            f"Post-failover pace: sleeping {wait:.1f}s before next request on "
            f"{self.active_model_id()}",
            file=sys.stderr,
        )
        time.sleep(wait)


_FAILOVER = GeminiFailoverManager()


def reset_model_failover_state() -> None:
    _FAILOVER.reset()


def active_model_quota() -> GeminiModelQuota:
    return _FAILOVER.active_quota()


def active_model_id() -> str:
    return _FAILOVER.active_model_id()


def try_advance_model(reason: str) -> bool:
    return _FAILOVER.try_advance(reason)


def pace_after_model_failover() -> None:
    _FAILOVER.pace_after_failover()


def _sleep_transient_backoff(attempt: int) -> None:
    time.sleep(2 ** (attempt - 1))


def is_daily_quota_error(body: str) -> bool:
    return bool(DAILY_QUOTA_RE.search(body or ""))


def parse_retry_after_seconds(response: requests.Response) -> float:
    header = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if header:
        try:
            return max(float(header), QUOTA_RETRY_DEFAULT_SEC)
        except ValueError:
            pass
    if match := RETRY_IN_RE.search(response.text or ""):
        try:
            return max(float(match.group(1)), 1.0)
        except ValueError:
            pass
    return QUOTA_RETRY_DEFAULT_SEC


def call_gemini(api_key: str, prompt: str) -> tuple[dict[str, Any], float]:
    """Send prompt to Gemini, return (api_payload, duration_seconds)."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    start = time.monotonic()
    quota_retries = transient_attempts = 0
    while True:
        model_id = active_model_id()
        url = gemini_endpoint(model_id)
        try:
            response = requests.post(url, json=body, headers=headers, timeout=HTTP_TIMEOUT_SEC)
        except requests.Timeout as exc:
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                raise RuntimeError(f"Gemini API timeout after {MAX_ATTEMPTS} attempts") from exc
            _sleep_transient_backoff(transient_attempts)
            continue
        except requests.RequestException as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc
        if response.status_code == 200:
            try:
                return response.json(), time.monotonic() - start
            except ValueError as exc:
                raise RuntimeError(f"Gemini returned non-JSON body: {response.text[:500]}") from exc
        if response.status_code == 429:
            text = response.text or ""
            if is_daily_quota_error(text):
                if try_advance_model(f"RPD/daily quota exhausted on {model_id}"):
                    quota_retries = transient_attempts = 0
                    pace_after_model_failover()
                    continue
                raise RuntimeError(
                    "Gemini RPD/daily quota exhausted on all models "
                    f"({', '.join(GEMINI_MODELS)}) — retry tomorrow or upgrade Usage Tier. "
                    f"Body: {text[:800]}"
                )
            wait = parse_retry_after_seconds(response)
            quota_retries += 1
            if quota_retries > MAX_QUOTA_RETRIES:
                if try_advance_model(f"RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} waits on {model_id}"):
                    quota_retries = transient_attempts = 0
                    pace_after_model_failover()
                    continue
                raise RuntimeError(
                    f"Gemini RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} waits on all models. "
                    f"Body: {text[:800]}"
                )
            print(
                f"HTTP 429 (RPM/TPM on {model_id}). Waiting {wait:.1f}s then auto-retry "
                f"({quota_retries}/{MAX_QUOTA_RETRIES}) — no need to reopen PR",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue
        if response.status_code in (500, 503):
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                if try_advance_model(
                    f"HTTP {response.status_code} after {MAX_ATTEMPTS} attempts on {model_id}"
                ):
                    quota_retries = transient_attempts = 0
                    pace_after_model_failover()
                    continue
                raise RuntimeError(
                    f"Gemini API failed with HTTP {response.status_code} on all models "
                    f"({', '.join(GEMINI_MODELS)}): {response.text[:1000]}"
                )
            print(
                f"HTTP {response.status_code} on {model_id}. "
                f"Retry {transient_attempts}/{MAX_ATTEMPTS} then failover if still failing",
                file=sys.stderr,
            )
            _sleep_transient_backoff(transient_attempts)
            continue
        raise RuntimeError(
            f"Gemini API failed with HTTP {response.status_code}: {response.text[:1000]}"
        )
