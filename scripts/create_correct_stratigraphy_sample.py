#!/usr/bin/env python3
"""
Create sample database with correct stratigraphic relationships
without paradoxes, following archaeological logic
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService
from pyarchinit_mini.services.periodizzazione_service import PeriodizzazioneService

def create_correct_stratigraphy_sample():
    """Create sample database with archaeologically correct stratigraphy"""
    
    # Database path
    db_path = os.path.join(project_root, 'pyarchinit_mini_sample.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database connection
    db_conn = DatabaseConnection(f'sqlite:///{db_path}')
    db_conn.create_tables()
    
    db_manager = DatabaseManager(db_conn)
    
    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    periodizzazione_service = PeriodizzazioneService(db_manager)
    
    print("Creating archaeologically correct sample database...")
    
    # 1. Create site
    site_data = {
        'sito': 'Sito Archeologico di Esempio',
        'comune': 'Roma',
        'provincia': 'RM', 
        'regione': 'Lazio',
        'nazione': 'Italia',
        'descrizione': 'Sito di esempio con stratigrafia corretta per dimostrazioni'
    }
    
    site = site_service.create_site(site_data)
    site_name = site_data['sito']  # Use the data directly instead of accessing the ORM object
    print(f"Created site: {site_name}")
    
    # 2. Create periods (skipped for now - no validator for periodizzazione yet)
    # TODO: Add periodizzazione validator and uncomment this section
    print("Skipping periods creation (no validator yet)")
    
    # 3. Create US with correct stratigraphic relationships
    # Following archaeological logic from bottom (oldest) to top (newest)
    
    us_list = []
    
    # Natural ground (oldest) - using 1000 instead of 0 due to validator constraint
    us_1000 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 1000,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Terreno vergine naturale',
        'd_interpretativa': 'Substrato geologico naturale',
        'periodo_iniziale': 'Preistorico',
        'fase_iniziale': 'Naturale',
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_1000)
    
    # Phase I - Foundation (Roman Imperial)
    # Foundation cuts
    us_10 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 10,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Taglio di fondazione per muro perimetrale',
        'd_interpretativa': 'Fossa di fondazione edificio principale',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'I - Fondazione',
        'rapporti': 'Taglia 1000',  # Cuts the natural ground
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_10)
    
    # Foundation walls
    us_11 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 11,
        'unita_tipo': 'USM',
        'd_stratigrafica': 'Muro perimetrale in opus reticulatum',
        'd_interpretativa': 'Muro perimetrale dell\'edificio principale',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'I - Fondazione',
        'rapporti': 'Riempie 10',  # Fills the foundation cut
        'stato_di_conservazione': 'Discreto',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_11)
    
    # Floor preparation
    us_12 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 12,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Preparazione pavimentale in cocciopesto',
        'd_interpretativa': 'Sottofondo per pavimentazione',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'I - Fondazione',
        'rapporti': 'Copre 1000; Si appoggia a 11',  # Covers natural ground, abuts wall
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_12)
    
    # Floor
    us_13 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 13,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Pavimento in opus tessellatum',
        'd_interpretativa': 'Pavimento musivo geometrico',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'I - Fondazione',
        'rapporti': 'Copre 12',  # Covers floor preparation
        'stato_di_conservazione': 'Discreto',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_13)
    
    # Phase II - Development
    # Use accumulation
    us_20 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 20,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Strato di accumulo con ceramica e ossa',
        'd_interpretativa': 'Livello d\'uso della fase II',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'II - Sviluppo',
        'rapporti': 'Copre 13',  # Covers the floor
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_20)
    
    # Repair cut
    us_21 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 21,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Taglio per riparazione pavimento',
        'd_interpretativa': 'Fossa per riparazione',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'II - Sviluppo',
        'rapporti': 'Taglia 13',  # Cuts the floor
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_21)
    
    # Repair fill
    us_22 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 22,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Riempimento con malta e frammenti laterizi',
        'd_interpretativa': 'Riparazione del pavimento',
        'periodo_iniziale': 'Età Romana Imperiale',
        'fase_iniziale': 'II - Sviluppo',
        'rapporti': 'Riempie 21; Coperto da 20',  # Fills repair cut, covered by use layer
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_22)
    
    # Phase III - Late Antique transformation
    # Destruction layer
    us_30 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 30,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Crollo di tegole e coppi',
        'd_interpretativa': 'Crollo del tetto',
        'periodo_iniziale': 'Tardo Antico',
        'fase_iniziale': 'III - Trasformazione',
        'rapporti': 'Copre 20, 11',  # Covers use layer and walls
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_30)
    
    # Leveling for new floor
    us_31 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 31,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Livellamento con macerie',
        'd_interpretativa': 'Preparazione per nuova pavimentazione',
        'periodo_iniziale': 'Tardo Antico',
        'fase_iniziale': 'III - Trasformazione',
        'rapporti': 'Copre 30',  # Covers collapse
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_31)
    
    # New beaten earth floor
    us_32 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 32,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Pavimento in terra battuta',
        'd_interpretativa': 'Pavimento povero di riuso',
        'periodo_iniziale': 'Tardo Antico',
        'fase_iniziale': 'III - Trasformazione',
        'rapporti': 'Copre 31',  # Covers leveling
        'stato_di_conservazione': 'Mediocre',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_32)
    
    # Phase IV - Abandonment
    # Final abandonment layer
    us_40 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 40,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Strato di abbandono con vegetazione',
        'd_interpretativa': 'Accumulo naturale post-abbandono',
        'periodo_iniziale': 'Alto Medioevo',
        'fase_iniziale': 'IV - Abbandono',
        'rapporti': 'Copre 32, 31, 11',  # Covers everything
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_40)
    
    # Phase V - Modern excavation
    # Topsoil
    us_1 = us_service.create_us({
        'sito': site_name,
        'area': 'A',
        'us': 1,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Humus superficiale',
        'd_interpretativa': 'Terreno agricolo moderno',
        'periodo_iniziale': 'Moderno',
        'fase_iniziale': 'V - Scavo',
        'rapporti': 'Copre 40',  # Covers abandonment
        'stato_di_conservazione': 'Buono',
        'scavato': 'Sì',
        'anno_scavo': datetime.now().year
    })
    us_list.append(us_1)
    
    print(f"Created {len(us_list)} US records with correct stratigraphic relationships")
    
    # 4. Create some finds
    finds = [
        {
            'sito': site_name,
            'numero_inventario': 1,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Terra sigillata',
            'area': 'A',
            'us': 20,
            'lavato': 'yes',
            'peso': 25.5,
            'descrizione': 'Frammento di parete con decorazione a rilievo'
        },
        {
            'sito': site_name,
            'numero_inventario': 2,
            'tipo_reperto': 'Metallo',
            'definizione': 'Moneta in bronzo',
            'area': 'A',
            'us': 20,
            'lavato': 'yes',
            'peso': 8.3,
            'descrizione': 'Asse di Traiano, buona conservazione'
        },
        {
            'sito': site_name,
            'numero_inventario': 3,
            'tipo_reperto': 'Osso',
            'definizione': 'Osso lavorato',
            'area': 'A',
            'us': 32,
            'lavato': 'yes',
            'peso': 12.1,
            'descrizione': 'Spillone in osso con testa decorata'
        },
        {
            'sito': site_name,
            'numero_inventario': 4,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Ceramica comune',
            'area': 'A',
            'us': 30,
            'lavato': 'yes',
            'peso': 156.7,
            'descrizione': 'Frammenti di olla da cucina'
        },
        {
            'sito': site_name,
            'numero_inventario': 5,
            'tipo_reperto': 'Pietra',
            'definizione': 'Frammento arch.',
            'area': 'A',
            'us': 30,
            'lavato': 'no',
            'peso': 2340.0,
            'descrizione': 'Frammento di cornice modanata in marmo'
        }
    ]
    
    for find_data in finds:
        inventario_service.create_inventario(find_data)
    print(f"Created {len(finds)} inventory items")
    
    # Close database connection
    db_conn.close()
    
    print(f"\nSample database created successfully at: {db_path}")
    print("\nStratigraphic sequence (from newest to oldest):")
    print("1 (Topsoil) → 40 (Abandonment) → 32 (Beaten earth floor) → 31 (Leveling)")
    print("→ 30 (Collapse) → 20 (Use layer) → 22 (Repair) → 13 (Floor) → 12 (Preparation)")
    print("→ 11 (Wall in cut 10) → 10 (Foundation cut) → 1000 (Natural)")
    print("\nNo stratigraphic paradoxes - all relationships follow archaeological logic!")
    
    return db_path

if __name__ == "__main__":
    create_correct_stratigraphy_sample()