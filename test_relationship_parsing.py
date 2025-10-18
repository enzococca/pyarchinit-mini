#!/usr/bin/env python3
"""
Test relationship parsing
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

# Connect to sample database
db_conn = DatabaseConnection.sqlite("data/pyarchinit_mini_sample.db")
db_manager = DatabaseManager(db_conn)

# Create services
us_service = USService(db_manager)

# Create matrix generator
generator = HarrisMatrixGenerator(db_manager, us_service)

# Get relationships
print("Testing relationship parsing...")
relationships = generator._get_relationships("Sito Archeologico di Esempio", area="A")

print(f"\nFound {len(relationships)} relationships")

# Show first 10
for i, rel in enumerate(relationships[:10]):
    print(f"{i+1}. US {rel['us_from']} {rel['type']} US {rel['us_to']}")

# Close connection
db_conn.close()

print("\n✓ Parsing test completed successfully!")
