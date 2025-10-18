#!/usr/bin/env python3
"""
Script per creare dati di esempio per testare la Web Interface di PyArchInit-Mini

Questo script crea:
- 3 siti archeologici di esempio
- 15 unità stratigrafiche con rapporti
- 10 reperti inventario
- Rapporti stratigrafici completi per generare Harris Matrix

Uso:
    python scripts/create_sample_for_webapp.py

Oppure:
    python scripts/create_sample_for_webapp.py --database custom_path.db
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService


def create_sample_data(db_path: str = 'data/pyarchinit_mini.db'):
    """Create sample data for web interface testing"""

    print(f"Creating sample data in: {db_path}")
    print("=" * 60)

    # Initialize database
    db_url = f'sqlite:///./{db_path}'
    db_conn = DatabaseConnection.from_url(db_url)
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)

    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)

    # ========================================
    # 1. CREATE SITES
    # ========================================
    print("\n1. Creating archaeological sites...")

    sites_data = [
        {
            'sito': 'Villa Romana di Positano',
            'nazione': 'Italia',
            'regione': 'Campania',
            'provincia': 'Salerno',
            'comune': 'Positano',
            'definizione_sito': 'Villa marittima romana',
            'descrizione': 'Villa romana con impianto termale del I secolo d.C. affacciata sul mare.'
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'nazione': 'Italia',
            'regione': 'Lazio',
            'provincia': 'Viterbo',
            'comune': 'Tarquinia',
            'definizione_sito': 'Area funeraria etrusca',
            'descrizione': 'Necropoli con tombe a camera affrescate, VII-II secolo a.C.'
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'nazione': 'Italia',
            'regione': 'Toscana',
            'provincia': 'Siena',
            'comune': 'Monteriggioni',
            'definizione_sito': 'Borgo fortificato medievale',
            'descrizione': 'Insediamento fortificato del XIII secolo con cinta muraria integra.'
        }
    ]

    created_sites = []
    for site_data in sites_data:
        try:
            site = site_service.create_site(site_data)
            created_sites.append(site)
            print(f"  ✓ Created site: {site_data['sito']}")
        except Exception as e:
            print(f"  ✗ Error creating site {site_data['sito']}: {e}")

    # ========================================
    # 2. CREATE US (Stratigraphic Units)
    # ========================================
    print("\n2. Creating stratigraphic units (US)...")

    # US for Villa Romana di Positano
    us_villa = [
        {
            'sito': 'Villa Romana di Positano',
            'area': 'Settore A',
            'us': 1001,
            'd_stratigrafica': 'Strato di humus superficiale',
            'd_interpretativa': 'Livello di calpestio moderno',
            'descrizione': 'Terreno vegetale scuro con radici moderne',
            'interpretazione': 'Livello di accumulo post-abbandono',
            'anno_scavo': 2023,
            'schedatore': 'Dr. Maria Rossi',
            'formazione': 'Natural',
            'rapporti': ''  # Top level
        },
        {
            'sito': 'Villa Romana di Positano',
            'area': 'Settore A',
            'us': 1002,
            'd_stratigrafica': 'Strato di crollo tegole',
            'd_interpretativa': 'Crollo tetto',
            'descrizione': 'Concentrazione di tegole e coppi frammentati',
            'interpretazione': 'Crollo della copertura dell\'edificio termale',
            'anno_scavo': 2023,
            'schedatore': 'Dr. Maria Rossi',
            'formazione': 'Artificial',
            'rapporti': 'copre 1003, copre 1004'
        },
        {
            'sito': 'Villa Romana di Positano',
            'area': 'Settore A',
            'us': 1003,
            'd_stratigrafica': 'Pavimento a mosaico',
            'd_interpretativa': 'Piano di calpestio',
            'descrizione': 'Pavimento in tessere bianche e nere con motivo geometrico',
            'interpretazione': 'Pavimento del frigidarium',
            'anno_scavo': 2023,
            'schedatore': 'Dr. Maria Rossi',
            'formazione': 'Artificial',
            'rapporti': 'si appoggia a 1005'
        },
        {
            'sito': 'Villa Romana di Positano',
            'area': 'Settore A',
            'us': 1004,
            'd_stratigrafica': 'Strato di cenere e carboni',
            'd_interpretativa': 'Livello di incendio',
            'descrizione': 'Strato compatto con abbondante carbone e cenere',
            'interpretazione': 'Livello di distruzione per incendio',
            'anno_scavo': 2023,
            'schedatore': 'Dr. Maria Rossi',
            'formazione': 'Artificial',
            'rapporti': 'copre 1005'
        },
        {
            'sito': 'Villa Romana di Positano',
            'area': 'Settore A',
            'us': 1005,
            'd_stratigrafica': 'Muro in opera reticolata',
            'd_interpretativa': 'Struttura perimetrale',
            'descrizione': 'Muro in blocchetti di tufo disposti a rombo',
            'interpretazione': 'Muro perimetrale dell\'ambiente termale',
            'anno_scavo': 2023,
            'schedatore': 'Dr. Maria Rossi',
            'formazione': 'Artificial',
            'rapporti': 'taglia 1006'
        },
    ]

    # US for Necropoli Etrusca
    us_necropoli = [
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'area': 'Tomba 12',
            'us': 2001,
            'd_stratigrafica': 'Riempimento camera sepolcrale',
            'd_interpretativa': 'Riempimento post-deposizionale',
            'descrizione': 'Terra marrone con frammenti ceramici',
            'interpretazione': 'Riempimento della camera dopo il crollo',
            'anno_scavo': 2023,
            'schedatore': 'Prof. Giovanni Bianchi',
            'formazione': 'Natural',
            'rapporti': 'copre 2002, copre 2003'
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'area': 'Tomba 12',
            'us': 2002,
            'd_stratigrafica': 'Intonaco affrescato',
            'd_interpretativa': 'Decorazione parietale',
            'descrizione': 'Frammenti di intonaco con pigmenti rossi e neri',
            'interpretazione': 'Affresco con scene di banchetto',
            'anno_scavo': 2023,
            'schedatore': 'Prof. Giovanni Bianchi',
            'formazione': 'Artificial',
            'rapporti': 'si appoggia a 2004'
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'area': 'Tomba 12',
            'us': 2003,
            'd_stratigrafica': 'Deposizione funeraria',
            'd_interpretativa': 'Corredo funerario',
            'descrizione': 'Concentrazione di vasi in bucchero e bronzi',
            'interpretazione': 'Corredo della sepoltura principale',
            'anno_scavo': 2023,
            'schedatore': 'Prof. Giovanni Bianchi',
            'formazione': 'Artificial',
            'rapporti': 'si appoggia a 2005'
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'area': 'Tomba 12',
            'us': 2004,
            'd_stratigrafica': 'Parete camera',
            'd_interpretativa': 'Struttura muraria',
            'descrizione': 'Parete in blocchi di tufo squadrati',
            'interpretazione': 'Parete della camera sepolcrale',
            'anno_scavo': 2023,
            'schedatore': 'Prof. Giovanni Bianchi',
            'formazione': 'Artificial',
            'rapporti': 'taglia 2006'
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'area': 'Tomba 12',
            'us': 2005,
            'd_stratigrafica': 'Banchina in pietra',
            'd_interpretativa': 'Letto funebre',
            'descrizione': 'Banchina in blocchi di tufo per deposizione',
            'interpretazione': 'Letto per la deposizione del defunto',
            'anno_scavo': 2023,
            'schedatore': 'Prof. Giovanni Bianchi',
            'formazione': 'Artificial',
            'rapporti': 'si appoggia a 2006'
        },
    ]

    # US for Monteriggioni
    us_monteriggioni = [
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'area': 'Torre Nord',
            'us': 3001,
            'd_stratigrafica': 'Crollo merlatura',
            'd_interpretativa': 'Crollo sommitale',
            'descrizione': 'Blocchi di pietra della merlatura',
            'interpretazione': 'Crollo della sommità della torre',
            'anno_scavo': 2023,
            'schedatore': 'Dott.ssa Laura Verdi',
            'formazione': 'Artificial',
            'rapporti': 'copre 3002'
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'area': 'Torre Nord',
            'us': 3002,
            'd_stratigrafica': 'Pavimento in cotto',
            'd_interpretativa': 'Piano di calpestio',
            'descrizione': 'Pavimento in mattoni disposti a spina di pesce',
            'interpretazione': 'Pavimento del piano superiore della torre',
            'anno_scavo': 2023,
            'schedatore': 'Dott.ssa Laura Verdi',
            'formazione': 'Artificial',
            'rapporti': 'si appoggia a 3003'
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'area': 'Torre Nord',
            'us': 3003,
            'd_stratigrafica': 'Muratura in pietra',
            'd_interpretativa': 'Struttura perimetrale torre',
            'descrizione': 'Muro in conci di pietra con malta di calce',
            'interpretazione': 'Muro perimetrale della torre',
            'anno_scavo': 2023,
            'schedatore': 'Dott.ssa Laura Verdi',
            'formazione': 'Artificial',
            'rapporti': 'taglia 3004'
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'area': 'Torre Nord',
            'us': 3004,
            'd_stratigrafica': 'Terreno vegetale',
            'd_interpretativa': 'Livello pre-costruzione',
            'descrizione': 'Terra scura con materiale ceramico sparso',
            'interpretazione': 'Livello precedente alla costruzione della torre',
            'anno_scavo': 2023,
            'schedatore': 'Dott.ssa Laura Verdi',
            'formazione': 'Natural',
            'rapporti': ''  # Base
        },
    ]

    all_us = us_villa + us_necropoli + us_monteriggioni

    created_us = []
    for us_data in all_us:
        try:
            us = us_service.create_us(us_data)
            created_us.append(us)
            print(f"  ✓ Created US {us_data['us']}: {us_data['d_stratigrafica']}")
        except Exception as e:
            print(f"  ✗ Error creating US {us_data['us']}: {e}")

    # ========================================
    # 3. CREATE INVENTORY (Reperti)
    # ========================================
    print("\n3. Creating inventory items...")

    inventory_data = [
        # Villa Romana
        {
            'sito': 'Villa Romana di Positano',
            'numero_inventario': 1001,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Anfora Dressel 20',
            'descrizione': 'Anfora per trasporto olio, orlo e collo frammentari',
            'area': 'Settore A',
            'us': 1002,
            'peso': 3500.0
        },
        {
            'sito': 'Villa Romana di Positano',
            'numero_inventario': 1002,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Tessera di mosaico',
            'descrizione': 'Tessera in pasta vitrea colore blu',
            'area': 'Settore A',
            'us': 1003,
            'peso': 15.5
        },
        {
            'sito': 'Villa Romana di Positano',
            'numero_inventario': 1003,
            'tipo_reperto': 'Metallo',
            'definizione': 'Chiodo in ferro',
            'descrizione': 'Chiodo con testa quadrata, ossidato',
            'area': 'Settore A',
            'us': 1002,
            'peso': 45.2
        },
        # Necropoli Etrusca
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'numero_inventario': 2001,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Kylix bucchero',
            'descrizione': 'Coppa per bere in bucchero nero lucidato, intero',
            'area': 'Tomba 12',
            'us': 2003,
            'peso': 280.0
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'numero_inventario': 2002,
            'tipo_reperto': 'Metallo',
            'definizione': 'Fibula in bronzo',
            'descrizione': 'Fibula ad arco serpeggiante con decorazione incisa',
            'area': 'Tomba 12',
            'us': 2003,
            'peso': 18.5
        },
        {
            'sito': 'Necropoli Etrusca di Tarquinia',
            'numero_inventario': 2003,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Oinochoe in bucchero',
            'descrizione': 'Brocca trilobata in bucchero grigio',
            'area': 'Tomba 12',
            'us': 2003,
            'peso': 450.0
        },
        # Monteriggioni
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'numero_inventario': 3001,
            'tipo_reperto': 'Ceramica',
            'definizione': 'Maiolica arcaica',
            'descrizione': 'Orlo di ciotola in maiolica con decorazione verde ramina',
            'area': 'Torre Nord',
            'us': 3002,
            'peso': 65.0
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'numero_inventario': 3002,
            'tipo_reperto': 'Metallo',
            'definizione': 'Punta di freccia',
            'descrizione': 'Punta di freccia in ferro a lama triangolare',
            'area': 'Torre Nord',
            'us': 3001,
            'peso': 25.0
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'numero_inventario': 3003,
            'tipo_reperto': 'Vetro',
            'definizione': 'Frammento bicchiere',
            'descrizione': 'Frammento di bicchiere in vetro soffiato verdastro',
            'area': 'Torre Nord',
            'us': 3002,
            'peso': 8.5
        },
        {
            'sito': 'Insediamento Medievale di Monteriggioni',
            'numero_inventario': 3004,
            'tipo_reperto': 'Pietra',
            'definizione': 'Macina in pietra',
            'descrizione': 'Frammento di macina circolare in arenaria',
            'area': 'Torre Nord',
            'us': 3004,
            'peso': 2500.0
        },
    ]

    created_inventory = []
    for inv_data in inventory_data:
        try:
            item = inventario_service.create_inventario(inv_data)
            created_inventory.append(item)
            print(f"  ✓ Created inventory {inv_data['numero_inventario']}: {inv_data['definizione']}")
        except Exception as e:
            print(f"  ✗ Error creating inventory {inv_data['numero_inventario']}: {e}")

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Sites created: {len(created_sites)}")
    print(f"✓ US created: {len(created_us)}")
    print(f"✓ Inventory items created: {len(created_inventory)}")
    print("\nDatabase ready at:", db_path)
    print("\nYou can now:")
    print("  1. Start web interface: python web_interface/app.py")
    print("  2. Access: http://localhost:5001")
    print("  3. Try Harris Matrix for any site")
    print("  4. Export PDF reports")
    print("  5. Create new US with stratigraphic relationships")


def main():
    parser = argparse.ArgumentParser(
        description='Create sample archaeological data for PyArchInit-Mini web interface'
    )
    parser.add_argument(
        '--database',
        default='data/pyarchinit_mini.db',
        help='Path to SQLite database file (default: data/pyarchinit_mini.db)'
    )

    args = parser.parse_args()

    # Ensure data directory exists
    db_dir = os.path.dirname(args.database)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    create_sample_data(args.database)


if __name__ == '__main__':
    main()
