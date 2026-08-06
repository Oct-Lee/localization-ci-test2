"""Data models for the Localization Quality Gate."""

from __future__ import annotations

from typing import Any, TypedDict


class Issue(TypedDict, total=False):
    original: str
    problem: str
    suggestion: str
    severity: str          # 'high', 'medium', 'low'
    file: str | None
    line: int | None
    # internal fields used during processing
    _kind: str | None
    _recover_original: bool | None
    _key_name: str | None


class FileStat(TypedDict):
    path: str
    added: int
    deleted: int


class AddedLine(TypedDict):
    line: int
    text: str


class DiffAnalysis(TypedDict, total=False):
    review_text: str
    review_by_file: dict[str, str]
    files: list[FileStat]
    _added_line_details: dict[str, list[AddedLine]]
