"""Database utilities — UUID v7 generation, etc."""
import time
import uuid as _uuid

try:
    # PyPI package name is `uuid7`, but the importable module is `uuid_extensions`.
    from uuid_extensions import uuid7 as _u7
except ImportError:
    _u7 = None


def generate_node_uuid() -> str:
    """Generate a UUID v7 (time-ordered) and return as canonical string.

    Time-ordered UUIDs are preferable to v4 for DB indexing — adjacent inserts
    cluster near each other on disk, reducing index-page rewrites.
    """
    if _u7 is not None:
        return str(_u7())
    # Fallback: synthesize UUID v7 manually if uuid_extensions is unavailable.
    # 48-bit Unix-ms timestamp, then version nibble (7), then random nibbles,
    # then variant nibble (8/9/a/b), then random tail.
    ts_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    ts_hex = f"{ts_ms:012x}"  # 12 hex chars = 48 bits
    rand_hex = _uuid.uuid4().hex
    # Format: ttttttttttttvrrr-srrr-rrrrrrrrrrrr → 8-4-(7+3)-(s+3)-12
    return (
        f"{ts_hex[:8]}-"
        f"{ts_hex[8:12]}-"
        f"7{rand_hex[1:4]}-"
        f"{(int(rand_hex[4], 16) & 0x3 | 0x8):x}{rand_hex[5:8]}-"
        f"{rand_hex[8:20]}"
    )
