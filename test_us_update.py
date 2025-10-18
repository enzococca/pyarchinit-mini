#!/usr/bin/env python3
"""
Test US update with DTO method
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService

# Connect to sample database
db_conn = DatabaseConnection.sqlite("data/pyarchinit_mini_sample.db")
db_manager = DatabaseManager(db_conn)

# Create service
us_service = USService(db_manager)

print("Testing US update_us_dto...")

# Get a US
us_dto = us_service.get_us_dto_by_id(1)
if us_dto:
    print(f"\n✓ Found US: {us_dto.us} - {us_dto.d_stratigrafica}")
    print(f"  Current rapporti: {us_dto.rapporti}")

    # Update it
    update_data = {
        "descrizione": "TEST: Descrizione aggiornata tramite DTO",
        "rapporti": "copre 1002, taglia 1005"
    }

    print(f"\n  Updating US {us_dto.us}...")
    updated_dto = us_service.update_us_dto(us_dto.id_us, update_data)

    if updated_dto:
        print(f"✓ US updated successfully!")
        print(f"  New description: {updated_dto.descrizione[:50]}...")
        print(f"  New rapporti: {updated_dto.rapporti}")
    else:
        print("✗ Failed to update US")
else:
    print("✗ US not found")

# Close connection
db_conn.close()

print("\n✅ Test completed!")
