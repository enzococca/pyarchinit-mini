import re
import time
from pyarchinit_mini.database.utils import generate_node_uuid


def test_generate_node_uuid_returns_string_uuid_v7():
    uid = generate_node_uuid()
    # UUID v7 format: 8-4-4-4-12 hex, version nibble = '7', variant nibble in {8,9,a,b}
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        uid
    ), f"Not UUID v7 shape: {uid}"


def test_uuid_v7_is_time_ordered():
    a = generate_node_uuid()
    time.sleep(0.001)  # Sleep 1ms to ensure different timestamp
    b = generate_node_uuid()
    assert a < b, f"UUID v7 must be time-ordered, got {a} >= {b}"
