#!/usr/bin/env python3
"""
Script semplificato per popolare il database con dati di esempio
- 1 sito archeologico
- 100 US con relazioni stratigrafiche 
- 50 materiali distribuiti tra le US
"""

import sys
import os
from datetime import datetime, date
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali
from pyarchinit_mini.models.harris_matrix import HarrisMatrix, USRelationships

# Sample data
ITALIAN_NAMES = [
    "Mario Rossi", "Giuseppe Bianchi", "Francesco Russo", "Antonio Colombo",
    "Marco Ricci", "Alessandro Romano", "Matteo Greco", "Lorenzo Costa"
]

def create_sample_data(clean_first=True):
    """Create all sample data"""
    
    # Initialize database connection
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'data', 'pyarchinit_mini_sample.db')
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Clean database if requested
    if clean_first and os.path.exists(db_path):
        print("Removing existing database...")
        os.remove(db_path)
        print("✓ Existing database removed")
    
    db_connection = DatabaseConnection.sqlite(db_path)
    
    # Create tables
    print("Initializing database schema...")
    db_connection.create_tables()
    print("✓ Database schema initialized")
    
    print("=" * 60)
    print("GENERATING ARCHAEOLOGICAL SAMPLE DATA")
    print("=" * 60)
    
    site_name = "Sito Archeologico di Esempio"
    areas = ["A", "B", "C", "D"]
    
    # Create site
    print("Creating sample site...")
    with db_connection.get_session() as session:
        site = Site(
            sito=site_name,
            nazione='Italia',
            regione='Lazio',
            comune='Roma',
            provincia='RM',
            definizione_sito='Scavo stratigrafico',
            descrizione='Sito archeologico di esempio con stratificazione completa',
            find_check=True
        )
        session.add(site)
        session.commit()
        print(f"✓ Created site: {site_name}")
    
    # Create 100 US records
    print("Creating 100 US records...")
    periods = ["Età del Bronzo", "Età del Ferro", "Età Romana", "Medioevo"]
    formations = ["Naturale", "Antropica", "Mista"]
    colors = ["Marrone", "Grigio", "Nero", "Giallo"]
    
    us_list = []
    for us_num in range(1, 101):
        area = random.choice(areas)
        period = random.choice(periods)
        
        with db_connection.get_session() as session:
            us_record = US(
                sito=site_name,
                area=area,
                us=us_num,
                d_stratigrafica=f"Strato archeologico US {us_num}",
                d_interpretativa=f"Deposito del periodo {period}",
                periodo_iniziale=period,
                periodo_finale=period,
                formazione=random.choice(formations),
                colore=random.choice(colors),
                scavato="Si",
                anno_scavo=random.randint(2020, 2024),
                data_schedatura=date.today(),
                schedatore=random.choice(ITALIAN_NAMES),
                quota_relativa=round(random.uniform(-5.0, 0.0), 2),
                datazione=period
            )
            session.add(us_record)
            session.commit()
            us_list.append(us_num)
        
        if us_num % 20 == 0:
            print(f"  Created {us_num} US records...")
    
    print(f"✓ Created {len(us_list)} US records")
    
    # Create stratigraphic relationships
    print("Creating stratigraphic relationships...")
    relationships_count = 0
    
    for i in range(len(us_list) - 1):
        if random.random() < 0.7:  # 70% chance of relationship
            us_above = us_list[i]
            us_below = us_list[i + 1]
            
            with db_connection.get_session() as session:
                # Harris Matrix entry
                matrix_rel = HarrisMatrix(
                    sito=site_name,
                    area=random.choice(areas),
                    us_sopra=us_above,
                    us_sotto=us_below,
                    tipo_rapporto="sopra"
                )
                session.add(matrix_rel)
                
                # Detailed relationship
                detailed_rel = USRelationships(
                    sito=site_name,
                    us_from=us_above,
                    us_to=us_below,
                    relationship_type="sopra",
                    certainty="certa",
                    description=f"US {us_above} sopra US {us_below}"
                )
                session.add(detailed_rel)
                session.commit()
                relationships_count += 1
    
    print(f"✓ Created {relationships_count} stratigraphic relationships")
    
    # Create 50 materials
    print("Creating 50 material records...")
    material_types = [
        "Ceramica comune", "Ceramica fine", "Vetro", "Bronzo", "Ferro",
        "Osso lavorato", "Pietra", "Moneta", "Laterizio", "Terra sigillata"
    ]
    
    materials_count = 0
    for inv_num in range(1, 51):
        us_context = random.choice(us_list)
        material_type = random.choice(material_types)
        area = random.choice(areas)
        
        with db_connection.get_session() as session:
            material = InventarioMateriali(
                sito=site_name,
                numero_inventario=inv_num,
                tipo_reperto=material_type,
                definizione=f"{material_type} - frammento",
                descrizione=f"Reperto {inv_num}: {material_type} da US {us_context}",
                area=area,
                us=str(us_context),
                lavato="Si",
                stato_conservazione="Buono",
                peso=round(random.uniform(5.0, 500.0), 1),
                repertato="Si",
                diagnostico=random.choice(["Si", "No"]),
                n_reperto=inv_num,
                years=random.randint(2020, 2024),
                schedatore=random.choice(ITALIAN_NAMES),
                totale_frammenti=random.randint(1, 10)
            )
            session.add(material)
            session.commit()
            materials_count += 1
        
        if inv_num % 10 == 0:
            print(f"  Created {inv_num} materials...")
    
    print(f"✓ Created {materials_count} material records")
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA GENERATION COMPLETED")
    print("=" * 60)
    print(f"✓ Site: {site_name}")
    print(f"✓ US Records: {len(us_list)}")
    print(f"✓ Relationships: {relationships_count}")
    print(f"✓ Materials: {materials_count}")
    print(f"✓ Database: {db_path}")
    print("\nDatabase populated successfully!")
    print("You can now test the PyArchInit-Mini application with sample data.")
    
    # Test cascade deletion note
    print("\n" + "-" * 60)
    print("CASCADE DELETION CONFIGURED:")
    print("When you delete a site, all related US and materials will be")
    print("automatically deleted due to the CASCADE foreign key constraints.")
    print("-" * 60)

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)