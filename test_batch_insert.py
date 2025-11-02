#!/usr/bin/env python3
"""
Test script for batch_insert functionality
"""

import os
import sys

# Set DATABASE_URL
os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.batch_insert_tool import batch_insert

# Test data: 5 US for testing
test_records = [
    {
        "sito": "Domus Pompeiana Test",
        "area": "1",
        "us": 1,
        "unita_tipo": "US",
        "definizione_stratigrafica": "Strato",
        "descrizione_stratigrafica": "Strato di lapilli grigi pomicei",
        "interpretazione": "Deposito eruttivo Vesuvio 79 d.C.",
        "periodo_iniziale": "Età romana imperiale"
    },
    {
        "sito": "Domus Pompeiana Test",
        "area": "1",
        "us": 2,
        "unita_tipo": "US",
        "definizione_stratigrafica": "Strato",
        "descrizione_stratigrafica": "Cenere vulcanica compatta",
        "interpretazione": "Surge piroclastico",
        "periodo_iniziale": "Età romana imperiale"
    },
    {
        "sito": "Domus Pompeiana Test",
        "area": "1",
        "us": 3,
        "unita_tipo": "US",
        "definizione_stratigrafica": "Strato",
        "descrizione_stratigrafica": "Pomici bianche",
        "interpretazione": "Prima fase eruttiva",
        "periodo_iniziale": "Età romana imperiale"
    },
    {
        "sito": "Domus Pompeiana Test",
        "area": "1",
        "us": 4,
        "unita_tipo": "US",
        "definizione_stratigrafica": "Strato",
        "descrizione_stratigrafica": "Terra bruna con inclusi di carbone",
        "interpretazione": "Strato di crollo tetto",
        "periodo_iniziale": "Età romana imperiale"
    },
    {
        "sito": "Domus Pompeiana Test",
        "area": "1",
        "us": 5,
        "unita_tipo": "US",
        "definizione_stratigrafica": "Strato",
        "descrizione_stratigrafica": "Pavimento in opus signinum",
        "interpretazione": "Pavimento atrio",
        "periodo_iniziale": "Età romana imperiale"
    }
]

print("Testing batch_insert with 5 US records...")
print("=" * 60)

# First: Create test site
from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data

site_result = insert_data(
    table="site_table",
    data={
        "sito": "Domus Pompeiana Test",
        "nazione": "Italia",
        "regione": "Campania",
        "comune": "Pompei",
        "descrizione": "Sito di test per batch insert"
    }
)

print(f"\nSite creation: {site_result.get('message')}")

# Test batch insert
result = batch_insert(
    table="us_table",
    records=test_records,
    validate_only=False,
    stop_on_error=False
)

print("\n" + "=" * 60)
print("BATCH INSERT RESULT:")
print("=" * 60)
print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")

if result.get('success'):
    print(f"Inserted count: {result.get('inserted_count')}")
    print(f"Inserted IDs: {result.get('inserted_ids')}")
else:
    print(f"Error: {result.get('error')}")
    if 'validation_errors' in result:
        print("\nValidation Errors:")
        for err in result['validation_errors']:
            print(f"  - Record {err.get('record_index')}: {err.get('message')}")

print("=" * 60)
