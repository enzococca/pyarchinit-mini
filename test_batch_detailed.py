#!/usr/bin/env python3
"""Test batch_insert with detailed error output"""

import os
import sys
import json

os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.batch_insert_tool import batch_insert

test_record = {
    "sito": "Test Date Field",
    "area": "1",
    "us": 9999,
    "unita_tipo": "US",
    "definizione_stratigrafica": "Strato",
    "data_schedatura": "2024-06-15",
    "schedatore": "Test User"
}

result = batch_insert(
    table="us_table",
    records=[test_record],
    validate_only=False,
    stop_on_error=False
)

print(json.dumps(result, indent=2, default=str))
