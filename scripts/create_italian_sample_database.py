#!/usr/bin/env python3
"""
Create Italian sample database with diverse stratigraphic relationships
and proper temporal ordering for Harris Matrix visualization
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService
from pyarchinit_mini.services.periodizzazione_service import PeriodizzazioneService

def create_italian_sample():
    """Create comprehensive Italian sample database"""
    
    # Database path
    db_path = os.path.join(project_root, 'data', 'pyarchinit_mini_italian.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database connection
    db_conn = DatabaseConnection(f'sqlite:///{db_path}')
    db_conn.create_tables()
    
    db_manager = DatabaseManager(db_conn)
    
    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    periodizzazione_service = PeriodizzazioneService(db_manager)
    
    print("Creating Italian archaeological sample database...")
    
    # 1. Create site
    site_data = {
        'sito': 'Villa Romana di Settefinestre',
        'comune': 'Orbetello',
        'provincia': 'Grosseto', 
        'regione': 'Toscana',
        'nazione': 'Italia',
        'definizione_sito': 'Villa romana con fasi dal I sec. a.C. al V sec. d.C.',
        'descrizione': 'Complesso archeologico di una villa romana con settore residenziale e produttivo, occupata dal I secolo a.C. fino al tardo impero con evidenze di rioccupazione altomedievale.'
    }
    
    site = site_service.create_site(site_data)
    site_name = site_data['sito']  # Use the original site name
    print(f"Created site: {site_name}")
    
    # 2. Periods are defined in the US data directly
    print("Using integrated chronological periods in US data")
    
    # 3. Create stratigraphic units with diverse Italian relationships
    # Design complex stratigraphy with temporal coherence
    
    us_data = [
        # PERIODO 5 - ALTOMEDIEVALE (più recente, sopra nella matrix)
        {
            'us': 1001, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Strato superficiale di humus',
            'd_interpretativa': 'Accumulo superficiale moderno',
            'descrizione': 'Sottile strato di terra scura con radici e materiale moderno',
            'interpretazione': 'Livello superficiale di formazione recente',
            'periodo_iniziale': 5, 'fase_iniziale': 1, 'datazione': 'Altomedievale',
            'rapporti': "[[\"copre\", \"US_1002\"], [\"copre\", \"US_1003\"]]"
        },
        {
            'us': 1002, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica', 
            'd_stratigrafica': 'Strato di crollo con tegole e laterizi',
            'd_interpretativa': 'Crollo del tetto altomedievale',
            'descrizione': 'Strato compatto di tegole, coppi e laterizi frammentati in matrice terrosa bruna',
            'interpretazione': 'Crollo delle coperture della fase altomedievale',
            'periodo_iniziale': 5, 'fase_iniziale': 1, 'datazione': 'Altomedievale',
            'rapporti': "[[\"coperto da\", \"US_1001\"], [\"si appoggia\", \"US_1004\"], [\"taglia\", \"US_1005\"]]"
        },
        {
            'us': 1003, 'sito': site_name, 'area': 'B', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Buca di spoliazione circolare',
            'd_interpretativa': 'Asportazione di elementi architettonici',
            'descrizione': 'Fossa circolare riempita di terra scura con frammenti lapidei',
            'interpretazione': 'Spoliazione di colonna o elemento architettonico',
            'periodo_iniziale': 5, 'fase_iniziale': 1, 'datazione': 'Altomedievale',
            'rapporti': "[[\"coperto da\", \"US_1001\"], [\"taglia\", \"US_1006\"], [\"taglia\", \"US_1007\"]]"
        },
        
        # PERIODO 4 - TARDOANTICO  
        {
            'us': 1004, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Pavimento in cocciopesto degradato',
            'd_interpretativa': 'Rifacimento tardoantico del pavimento',
            'descrizione': 'Superficie pavimentale in cocciopesto molto rovinata con lacune',
            'interpretazione': 'Pavimentazione di fase tardoantica con segni di degrado',
            'periodo_iniziale': 4, 'fase_iniziale': 1, 'datazione': 'Tardoantico',
            'rapporti': "[[\"gli si appoggia\", \"US_1002\"], [\"copre\", \"US_1008\"], [\"uguale a\", \"US_1009\"]]"
        },
        
        # PERIODO 3 - TARDO IMPERO
        {
            'us': 1005, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Muro in opera listata',
            'd_interpretativa': 'Struttura muraria di III secolo',
            'descrizione': 'Muro in filari alternati di tufelli e laterizi con malta bianca',
            'interpretazione': 'Muro perimetrale della fase tardo imperiale',
            'periodo_iniziale': 3, 'fase_iniziale': 1, 'datazione': 'Tardo Impero',
            'rapporti': "[[\"tagliato da\", \"US_1002\"], [\"si lega a\", \"US_1010\"], [\"copre\", \"US_1011\"]]"
        },
        {
            'us': 1006, 'sito': site_name, 'area': 'B', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Pavimento in opus tessellatum',
            'd_interpretativa': 'Mosaico geometrico di III secolo',
            'descrizione': 'Pavimento musivo con tessere bianche e nere a motivo geometrico',
            'interpretazione': 'Pavimentazione musiva del triclinio',
            'periodo_iniziale': 3, 'fase_iniziale': 1, 'datazione': 'Tardo Impero',
            'rapporti': "[[\"tagliato da\", \"US_1003\"], [\"si appoggia\", \"US_1012\"], [\"copre\", \"US_1013\"]]"
        },
        {
            'us': 1007, 'sito': site_name, 'area': 'B', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Soglia in travertino',
            'd_interpretativa': 'Accesso tra ambienti',
            'descrizione': 'Blocco di travertino sagomato con incavi per cardini',
            'interpretazione': 'Soglia di passaggio tra il triclinio e l\'atrio',
            'periodo_iniziale': 3, 'fase_iniziale': 1, 'datazione': 'Tardo Impero',
            'rapporti': "[[\"tagliato da\", \"US_1003\"], [\"si lega a\", \"US_1006\"], [\"si appoggia\", \"US_1012\"]]"
        },
        
        # PERIODO 2 - MEDIO IMPERO
        {
            'us': 1008, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Livello di preparazione in cocciopesto',
            'd_interpretativa': 'Preparazione per pavimento',
            'descrizione': 'Strato di cocciopesto e malta per preparazione pavimentale',
            'interpretazione': 'Preparazione per il pavimento tardoantico',
            'periodo_iniziale': 2, 'fase_iniziale': 2, 'datazione': 'Medio Impero',
            'rapporti': "[[\"coperto da\", \"US_1004\"], [\"copre\", \"US_1014\"], [\"riempie\", \"US_1015\"]]"
        },
        {
            'us': 1009, 'sito': site_name, 'area': 'C', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Pavimento in opus spicatum',
            'd_interpretativa': 'Pavimentazione in laterizi a spina di pesce',
            'descrizione': 'Pavimento in mattoni disposti a spina di pesce',
            'interpretazione': 'Pavimentazione dell\'area di servizio',
            'periodo_iniziale': 2, 'fase_iniziale': 2, 'datazione': 'Medio Impero',
            'rapporti': "[[\"uguale a\", \"US_1004\"], [\"si appoggia\", \"US_1016\"], [\"copre\", \"US_1017\"]]"
        },
        {
            'us': 1010, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Muro in opera reticolata',
            'd_interpretativa': 'Struttura muraria di II secolo',
            'descrizione': 'Muro in opera reticolata con angoli in laterizio',
            'interpretazione': 'Muro perimetrale della fase medio imperiale',
            'periodo_iniziale': 2, 'fase_iniziale': 2, 'datazione': 'Medio Impero',
            'rapporti': "[[\"si lega a\", \"US_1005\"], [\"copre\", \"US_1018\"], [\"si appoggia\", \"US_1019\"]]"
        },
        
        # PERIODO 2 - ALTO IMPERO
        {
            'us': 1011, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Strato di livellamento con anfore',
            'd_interpretativa': 'Rialzamento del piano di calpestio',
            'descrizione': 'Strato di terra e frammenti anforici per livellamento',
            'interpretazione': 'Preparazione per la fase di ristrutturazione',
            'periodo_iniziale': 2, 'fase_iniziale': 1, 'datazione': 'Alto Impero',
            'rapporti': "[[\"coperto da\", \"US_1005\"], [\"copre\", \"US_1020\"], [\"riempito da\", \"US_1021\"]]"
        },
        {
            'us': 1012, 'sito': site_name, 'area': 'B', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Fondazione in opera cementizia',
            'd_interpretativa': 'Fondazioni della villa di I secolo',
            'descrizione': 'Gettata di calcestruzzo con inclusi lapidei di grandi dimensioni',
            'interpretazione': 'Fondazioni della villa nella fase alto imperiale',
            'periodo_iniziale': 2, 'fase_iniziale': 1, 'datazione': 'Alto Impero',
            'rapporti': "[[\"gli si appoggia\", \"US_1006\"], [\"gli si appoggia\", \"US_1007\"], [\"si appoggia\", \"US_1022\"]]"
        },
        
        # PERIODO 1 - AUGUSTEO/TARDO REPUBBLICANO (più antico, sotto nella matrix)
        {
            'us': 1013, 'sito': site_name, 'area': 'B', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Antropica',
            'd_stratigrafica': 'Pavimento in opus signinum',
            'd_interpretativa': 'Pavimentazione della prima fase',
            'descrizione': 'Pavimento in cocciopesto con inserti marmorei',
            'interpretazione': 'Pavimentazione della villa augustea',
            'periodo_iniziale': 1, 'fase_iniziale': 2, 'datazione': 'Augusteo',
            'rapporti': "[[\"coperto da\", \"US_1006\"], [\"si appoggia\", \"US_1023\"], [\"copre\", \"US_1024\"]]"
        },
        {
            'us': 1020, 'sito': site_name, 'area': 'A', 'anno_scavo': 2024,
            'unita_tipo': 'US', 'formazione': 'Naturale',
            'd_stratigrafica': 'Strato argilloso sterile',
            'd_interpretativa': 'Terreno naturale pre-insediamento',
            'descrizione': 'Argilla compatta giallastra sterile di materiali archeologici',
            'interpretazione': 'Terreno naturale prima dell\'impianto della villa',
            'periodo_iniziale': 1, 'fase_iniziale': 1, 'datazione': 'Tardo Repubblicano',
            'rapporti': "[[\"coperto da\", \"US_1011\"]]"
        }
    ]
    
    # Create US records
    created_us = []
    for us_item in us_data:
        us = us_service.create_us(us_item)
        created_us.append(us)
        print(f"Created US {us_item['us']}: {us_item['d_interpretativa']}")
    
    # 4. Create inventory finds with contextual information
    inventory_data = [
        # Materiali altomedievali
        {
            'numero_inventario': 1, 'sito': site_name, 'area': 'A', 'us': 1002,
            'tipo_reperto': 'Ceramica', 'definizione': 'Orlo di olletta',
            'descrizione': 'Frammento di orlo di olletta in ceramica comune depurata grigia con decorazione a onde',
            'corpo_ceramico': 'Ceramica comune', 'peso': 15, 'stato_conservazione': 'Frammentario',
            'datazione_reperto': 'VII-VIII sec. d.C.', 'criterio_schedatura': 'Sistematico'
        },
        # Materiali tardoantichi  
        {
            'numero_inventario': 2, 'sito': site_name, 'area': 'A', 'us': 1004, 
            'tipo_reperto': 'Ceramica', 'definizione': 'African Red Slip',
            'descrizione': 'Frammento di coppa in terra sigillata africana con decorazione a rilievo',
            'corpo_ceramico': 'Terra sigillata', 'peso': 25, 'stato_conservazione': 'Buono',
            'datazione_reperto': 'IV-V sec. d.C.', 'criterio_schedatura': 'Sistematico'
        },
        # Materiali tardo imperiali
        {
            'numero_inventario': 3, 'sito': site_name, 'area': 'B', 'us': 1006,
            'tipo_reperto': 'Tessera musiva', 'definizione': 'Tessera musiva',
            'descrizione': 'Tessera quadrangolare in pietra calcarea bianca per mosaico',
            'corpo_ceramico': 'Pietra', 'peso': 3, 'stato_conservazione': 'Integro',
            'datazione_reperto': 'III sec. d.C.', 'criterio_schedatura': 'Campionamento'
        },
        # Materiali medio imperiali
        {
            'numero_inventario': 4, 'sito': site_name, 'area': 'A', 'us': 1008,
            'tipo_reperto': 'Laterizio', 'definizione': 'Tegola',
            'descrizione': 'Frammento di tegola con bollo rettangolare parzialmente leggibile',
            'corpo_ceramico': 'Terracotta', 'peso': 185, 'stato_conservazione': 'Frammentario',
            'datazione_reperto': 'II sec. d.C.', 'criterio_schedatura': 'Sistematico'
        },
        # Materiali alto imperiali
        {
            'numero_inventario': 5, 'sito': site_name, 'area': 'B', 'us': 1012,
            'tipo_reperto': 'Ceramica', 'definizione': 'Anfora Dressel 20',
            'descrizione': 'Frammento di parete di anfora olearia betica Dressel 20',
            'corpo_ceramico': 'Ceramica comune', 'peso': 95, 'stato_conservazione': 'Frammentario',
            'datazione_reperto': 'I-II sec. d.C.', 'criterio_schedatura': 'Sistematico'
        },
        # Materiali augustei
        {
            'numero_inventario': 6, 'sito': site_name, 'area': 'B', 'us': 1013,
            'tipo_reperto': 'Ceramica', 'definizione': 'Coppa TSI',
            'descrizione': 'Coppa frammentaria in terra sigillata italica con decorazione vegetale',
            'corpo_ceramico': 'Terra sigillata', 'peso': 35, 'stato_conservazione': 'Frammentario',
            'datazione_reperto': 'I sec. a.C. - I sec. d.C.', 'criterio_schedatura': 'Sistematico'
        }
    ]
    
    # Create inventory records
    for inv_data in inventory_data:
        inventory = inventario_service.create_inventario(inv_data)
        print(f"Created inventory {inv_data['numero_inventario']}: {inv_data['definizione']}")
    
    print(f"\\n✅ Italian archaeological database created successfully!")
    print(f"📍 Location: {db_path}")
    print(f"🏛️ Site: {site_name}")
    print(f"📊 Stratigraphic Units: {len(us_data)}")
    print(f"🏺 Inventory Items: {len(inventory_data)}")
    print(f"⏰ Chronological Periods: 7 periods (integrated in US data)")
    
    print("\\n🔗 Stratigraphic relationships include:")
    print("   • copre/coperto da (covers/covered by)")
    print("   • taglia/tagliato da (cuts/cut by)")
    print("   • si appoggia/gli si appoggia (leans against)")
    print("   • si lega a (bonds to)")
    print("   • uguale a (same as)")
    print("   • riempie/riempito da (fills/filled by)")
    
    return db_path

if __name__ == "__main__":
    create_italian_sample()