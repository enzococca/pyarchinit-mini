#!/usr/bin/env python3
"""
Create sample database with 50 US and stratigraphic relationships
Single site, single area
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.periodizzazione_service import PeriodizzazioneService
from pyarchinit_mini.models.harris_matrix import Period, Periodizzazione
import random

def create_sample_database():
    """Create a sample database with realistic stratigraphic sequence"""

    # Create database
    db_path = os.path.join("data", "pyarchinit_mini_sample.db")

    # Remove existing database if present
    if os.path.exists(db_path):
        os.remove(db_path)

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create connection
    db_conn = DatabaseConnection.sqlite(db_path)
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    db_manager.run_migrations()

    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    period_service = PeriodizzazioneService(db_manager)

    print("Creating site...")
    # Create site
    site_data = {
        "sito": "Sito Archeologico di Esempio",
        "nazione": "Italia",
        "regione": "Lazio",
        "comune": "Roma",
        "provincia": "RM",
        "descrizione": "Sito archeologico di esempio con sequenza stratigrafica completa"
    }
    site = site_service.create_site(site_data)
    site_name = site_data["sito"]  # Use the site name from data, not from model
    print(f"✓ Created site: {site_name}")

    # Define area
    area = "A"

    # Create archaeological periods
    print("\nCreating archaeological periods...")
    periods_data = [
        {
            "period_name": "Romano Repubblicano",
            "phase_name": "Tardo Repubblicano",
            "start_date": -509,
            "end_date": -27,
            "description": "Periodo della Repubblica Romana",
            "chronology": "Roma antica"
        },
        {
            "period_name": "Romano Imperiale",
            "phase_name": "Alto Impero",
            "start_date": -27,
            "end_date": 284,
            "description": "Periodo imperiale romano (Alto Impero)",
            "chronology": "Roma antica"
        },
        {
            "period_name": "Romano Imperiale",
            "phase_name": "Tardo Impero",
            "start_date": 284,
            "end_date": 476,
            "description": "Periodo imperiale romano (Tardo Impero)",
            "chronology": "Roma antica"
        },
        {
            "period_name": "Medievale",
            "phase_name": "Alto Medioevo",
            "start_date": 476,
            "end_date": 1000,
            "description": "Periodo medievale antico",
            "chronology": "Medioevo"
        },
        {
            "period_name": "Medievale",
            "phase_name": "Basso Medioevo",
            "start_date": 1000,
            "end_date": 1492,
            "description": "Periodo medievale recente",
            "chronology": "Medioevo"
        }
    ]

    created_periods = []
    for period_data in periods_data:
        try:
            # Create period directly with db_manager
            period = db_manager.create(Period, period_data)
            created_periods.append(period)
        except Exception as e:
            # Period might already exist, skip
            print(f"  Note: {e}")
            pass

    print(f"✓ Created/verified {len(periods_data)} archaeological periods")

    # Create 50 US with realistic stratigraphy
    print("\nCreating 50 US with stratigraphic relationships...")

    us_list = []

    # Layer types
    layer_types = [
        ("Superficial", "Humus", "Strato superficiale di humus"),
        ("Topsoil", "Terreno arativo", "Strato di aratura moderna"),
        ("Collapse", "Crollo", "Crollo di strutture murarie"),
        ("Floor", "Pavimento", "Superficie pavimentale"),
        ("Fill", "Riempimento", "Riempimento di fossa"),
        ("Wall", "Muro", "Struttura muraria"),
        ("Cut", "Taglio", "Interfaccia di taglio"),
        ("Deposit", "Deposito", "Deposito archeologico"),
        ("Destruction", "Distruzione", "Livello di distruzione"),
        ("Construction", "Costruzione", "Livello di costruzione"),
    ]

    # Define chronological distribution (older at bottom, newer at top)
    # US 1001-1015: Medievale (top, most recent)
    # US 1016-1035: Romano Imperiale (middle)
    # US 1036-1050: Romano Repubblicano (bottom, oldest)

    chronology_mapping = {
        "Medievale": {
            "periodo_iniziale": "Medievale",
            "fase_iniziale": random.choice(["Alto Medioevo", "Basso Medioevo"]),
            "periodo_finale": "Medievale",
            "fase_finale": "Basso Medioevo",
            "datazione": "476-1492 d.C."
        },
        "Romano Imperiale": {
            "periodo_iniziale": "Romano Imperiale",
            "fase_iniziale": "Alto Impero",
            "periodo_finale": "Romano Imperiale",
            "fase_finale": "Tardo Impero",
            "datazione": "27 a.C. - 476 d.C."
        },
        "Romano Repubblicano": {
            "periodo_iniziale": "Romano Repubblicano",
            "fase_iniziale": "Tardo Repubblicano",
            "periodo_finale": "Romano Repubblicano",
            "fase_finale": "Tardo Repubblicano",
            "datazione": "509-27 a.C."
        }
    }

    # Create US from 1001 to 1050 (top to bottom chronologically)
    for i in range(50):
        us_num = 1001 + i

        # Assign chronology based on depth
        if i < 15:  # US 1001-1015
            chronology = "Medievale"
        elif i < 35:  # US 1016-1035
            chronology = "Romano Imperiale"
        else:  # US 1036-1050
            chronology = "Romano Repubblicano"

        chrono_data = chronology_mapping[chronology]

        # Select layer type based on position
        layer_type_idx = i % len(layer_types)
        layer_cat, layer_name, layer_desc_base = layer_types[layer_type_idx]

        # Create descriptive data
        us_data = {
            "sito": site_name,
            "area": area,
            "us": us_num,
            "unita_tipo": "US" if "Muro" not in layer_name else "USM",
            "d_stratigrafica": f"{layer_name} - {layer_desc_base}",
            "d_interpretativa": f"Interpretazione: {layer_cat.lower()}. Contesto {chronology.lower()}.",
            "descrizione": f"Descrizione dettagliata dello strato US {us_num}. "
                          f"{layer_desc_base}. Caratteristiche specifiche della US. "
                          f"Datazione: {chrono_data['datazione']}",
            "scavato": random.choice(["Sì", "No", "Parzialmente"]),
            "anno_scavo": 2024,
            "metodo_di_scavo": random.choice(["Manuale", "Meccanico", "Misto"]),
            "schedatore": "Archeologo di Esempio",
            "formazione": random.choice(["Naturale", "Artificiale", "Mista"]),
            "stato_di_conservazione": random.choice(["Ottimo", "Buono", "Discreto", "Cattivo"]),
            "colore": random.choice(["Marrone", "Grigio", "Nero", "Rossiccio", "Giallastro"]),
            "consistenza": random.choice(["Compatta", "Semicompatta", "Sciolta"]),
            # Chronological data
            "periodo_iniziale": chrono_data["periodo_iniziale"],
            "fase_iniziale": chrono_data["fase_iniziale"],
            "periodo_finale": chrono_data["periodo_finale"],
            "fase_finale": chrono_data["fase_finale"],
            "datazione": chrono_data["datazione"],
            "affidabilita": random.choice(["alta", "media", "alta"]),  # Mostly alta
            "rapporti": ""  # Will be filled later
        }

        # Create US
        us_service.create_us(us_data)
        # Store only US number for relationship building
        us_list.append(us_num)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/50 US...")

    print(f"✓ Created 50 US (1001-1050)")

    # Build stratigraphic relationships
    print("\nBuilding stratigraphic relationships...")

    relationship_count = 0

    # Create realistic relationships
    # Each US covers 1-3 later US (except the last ones)
    for i, us_num in enumerate(us_list):
        relationships = []

        # Don't create relationships for the last 5 US (bottom layers)
        if i < len(us_list) - 5:
            # Each US covers 1-3 subsequent US
            num_covers = random.randint(1, min(3, len(us_list) - i - 1))

            for j in range(1, num_covers + 1):
                if i + j < len(us_list):
                    covered_us_num = us_list[i + j]
                    relationships.append(f"Copre {covered_us_num}")
                    relationship_count += 1

        # Some US also have "si appoggia a" relationships
        if i > 0 and random.random() < 0.3:  # 30% chance
            supports_us_num = us_list[i - 1]
            relationships.append(f"Si appoggia a {supports_us_num}")
            relationship_count += 1

        # Some US cut others
        if i > 10 and random.random() < 0.2:  # 20% chance after US 1010
            cut_target_num = random.choice(us_list[i+1:min(i+5, len(us_list))])
            relationships.append(f"Taglia {cut_target_num}")
            relationship_count += 1

        # Update US with relationships - find by sito, area, us
        if relationships:
            rapporti_str = ", ".join(relationships)
            # Get US by sito, area, and us number using session
            from pyarchinit_mini.models.us import US
            with db_conn.get_session() as session:
                us_record = session.query(US).filter(
                    US.sito == site_name,
                    US.area == area,
                    US.us == us_num
                ).first()
                if us_record:
                    us_id = us_record.id_us
            # Update outside the session
            us_service.update_us(us_id, {"rapporti": rapporti_str})

    print(f"✓ Created {relationship_count} stratigraphic relationships")

    # Create Periodizzazione records for each US
    print("\nCreating periodization assignments...")
    periodization_count = 0

    for i, us_num in enumerate(us_list):
        # Determine chronology
        if i < 15:
            chronology = "Medievale"
            periodo_iniziale = "Medievale"
            fase_iniziale = random.choice(["Alto Medioevo", "Basso Medioevo"])
            periodo_finale = "Medievale"
            fase_finale = "Basso Medioevo"
            datazione_estesa = "476-1492 d.C. Contesto medievale con ceramica tipica del periodo."
            cultura = random.choice(["Longobarda", "Carolingia", "Comunale"])
        elif i < 35:
            chronology = "Romano Imperiale"
            periodo_iniziale = "Romano Imperiale"
            fase_iniziale = "Alto Impero"
            periodo_finale = "Romano Imperiale"
            fase_finale = "Tardo Impero"
            datazione_estesa = "27 a.C. - 476 d.C. Materiale ceramico e numismatico imperiale."
            cultura = random.choice(["Romana Imperiale", "Tardo Romana"])
        else:
            chronology = "Romano Repubblicano"
            periodo_iniziale = "Romano Repubblicano"
            fase_iniziale = "Tardo Repubblicano"
            periodo_finale = "Romano Repubblicano"
            fase_finale = "Tardo Repubblicano"
            datazione_estesa = "509-27 a.C. Ceramica a vernice nera e materiale repubblicano."
            cultura = "Romana Repubblicana"

        # Create periodizzazione record
        period_data = {
            "sito": site_name,
            "area": area,
            "us": us_num,
            "periodo_iniziale": periodo_iniziale,
            "fase_iniziale": fase_iniziale,
            "periodo_finale": periodo_finale,
            "fase_finale": fase_finale,
            "datazione_estesa": datazione_estesa,
            "motivazione": f"Datazione basata su analisi stratigrafica e materiale ceramico. US {us_num}.",
            "cultura": cultura,
            "affidabilita": random.choice(["alta", "media", "alta"]),
            "note": f"Periodizzazione US {us_num} - {chronology}"
        }

        try:
            # Create periodizzazione directly with db_manager
            db_manager.create(Periodizzazione, period_data)
            periodization_count += 1
        except Exception as e:
            print(f"  Warning: Could not create periodization for US {us_num}: {e}")

    print(f"✓ Created {periodization_count} periodization assignments")

    # Close connection
    db_conn.close()

    print(f"\n{'='*60}")
    print(f"✅ Sample database created successfully!")
    print(f"{'='*60}")
    print(f"Location: {os.path.abspath(db_path)}")
    print(f"\nContents:")
    print(f"  • 1 Archaeological Site: {site_name}")
    print(f"  • 50 Stratigraphic Units (US 1001-1050)")
    print(f"  • Area: {area}")
    print(f"  • {relationship_count} Stratigraphic Relationships")
    print(f"  • {len(periods_data)} Archaeological Periods")
    print(f"  • {periodization_count} Periodization Assignments")
    print(f"\nChronological distribution:")
    print(f"  • US 1001-1015: Medievale (476-1492 d.C.)")
    print(f"  • US 1016-1035: Romano Imperiale (27 a.C. - 476 d.C.)")
    print(f"  • US 1036-1050: Romano Repubblicano (509-27 a.C.)")
    print(f"\nYou can load this database from:")
    print(f"  Desktop GUI > File > Carica Database di Esempio")
    print(f"{'='*60}")

if __name__ == "__main__":
    create_sample_database()