"""Split review text into batches suitable for Gemini API."""

from config import (
    CONTEXT_LINES,
    FOCUSED_TARGET_BATCHES,
    MAX_REVIEW_CHARS,
    PACKED_MAX_CHUNKS_PER_BATCH,
    SHORT_FILE_MAX_CHARS,
    SHORT_FILE_MAX_CHUNKS,
    _FOCUSED_PATH_RE,
)

def prefers_focused_batches(path: str, review_text: str) -> bool:
    """Chinese/PT locale paths, or short files: use focused batching."""
    if _FOCUSED_PATH_RE.search(path or ""):
        return True
    chunks = review_chunks(review_text)
    return (
        0 < len(chunks) <= SHORT_FILE_MAX_CHUNKS
        and len(review_text) <= SHORT_FILE_MAX_CHARS
    )

def review_chunks(review_text: str) -> list[str]:
    return [c for c in review_text.split("\n\n") if c.strip()]

def focused_max_chunks_per_batch(chunk_count: int) -> int:
    if chunk_count <= 0:
        return 1
    if chunk_count <= FOCUSED_TARGET_BATCHES:
        return chunk_count
    by_target = (chunk_count + FOCUSED_TARGET_BATCHES - 1) // FOCUSED_TARGET_BATCHES
    return min(by_target, PACKED_MAX_CHUNKS_PER_BATCH)

def max_chunks_per_batch_for_file(path: str, review_text: str) -> int | None:
    chunks = review_chunks(review_text)
    if prefers_focused_batches(path, review_text):
        return focused_max_chunks_per_batch(len(chunks))
    if len(chunks) > PACKED_MAX_CHUNKS_PER_BATCH:
        return PACKED_MAX_CHUNKS_PER_BATCH
    return None

def split_into_batches(
    review_text: str,
    limit: int | None = None,
    *,
    max_chunks_per_batch: int | None = None,
) -> list[str]:
    """Pack whole review chunks (separated by \n\n)."""
    if limit is None:
        limit = MAX_REVIEW_CHARS
    if not review_text.strip():
        return []
    chunks = review_chunks(review_text)
    if not chunks:
        return []
    if max_chunks_per_batch is not None and max_chunks_per_batch <= 0:
        raise ValueError("max_chunks_per_batch must be positive when set")
    batches: list[str] = []
    current: list[str] = []
    current_len = 0
    sep = "\n\n"

    def flush() -> None:
        nonlocal current, current_len
        if current:
            batches.append(sep.join(current))
            current, current_len = [], 0

    for chunk in chunks:
        if len(chunk) > limit:
            flush()
            hard = split_text_for_limit(chunk, limit)
            # Overlap last CONTEXT_LINES of previous hard piece into the next.
            for i, piece in enumerate(hard):
                if i == 0:
                    batches.append(piece)
                    continue
                prev_tail = "\n".join(hard[i - 1].splitlines()[-CONTEXT_LINES:])
                merged = f"{prev_tail}\n{piece}" if prev_tail else piece
                if len(merged) <= limit:
                    batches.append(merged)
                else:
                    batches.append(piece)
            continue
        add_len = len(chunk) + (len(sep) if current else 0)
        chunk_cap = (
            max_chunks_per_batch is not None and len(current) >= max_chunks_per_batch
        )
        if current and (current_len + add_len > limit or chunk_cap):
            flush()
        current.append(chunk)
        current_len += len(chunk) + (len(sep) if current_len else 0)
    flush()
    return batches

def split_text_for_limit(text: str, limit: int) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    if not text:
        return []
    if len(text) <= limit:
        return [text]
    pieces, start, n = [], 0, len(text)
    while start < n:
        remaining = n - start
        if remaining <= limit:
            pieces.append(text[start:])
            break
        window_end = start + limit
        cut = text.rfind("\n\n", start + 1, window_end + 1)
        if cut > start:
            cut += 2
        else:
            cut = text.rfind("\n", start + 1, window_end + 1)
            cut = cut + 1 if cut > start else window_end
        pieces.append(text[start:cut])
        start = cut
    return pieces

def with_batch_continuation_header(path: str, batch: str, *, batch_index: int) -> str:
    """Add [path] header if batch doesn't start with a file marker."""
    stripped = batch.lstrip()
    if batch_index == 0 or stripped.startswith("["):
        return batch
    return f"[{path}]\n\n{batch}"
