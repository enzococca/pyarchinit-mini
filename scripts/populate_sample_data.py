#!/usr/bin/env python3
"""
Script per popolare il database con dati di esempio
- 1 sito archeologico
- 100 US con relazioni stratigrafiche 
- 50 materiali distribuiti tra le US
- Thesaurus completo
"""

import sys
import os
from datetime import datetime, date
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali
from pyarchinit_mini.models.harris_matrix import HarrisMatrix, USRelationships, Period, Periodizzazione
from pyarchinit_mini.models.thesaurus import ThesaurusSigle, ThesaurusField, THESAURUS_MAPPINGS

# Sample Italian names for realistic data
ITALIAN_NAMES = [
    "Mario Rossi", "Giuseppe Bianchi", "Francesco Russo", "Antonio Colombo",
    "Marco Ricci", "Alessandro Romano", "Matteo Greco", "Lorenzo Costa",
    "Andrea Ferrari", "Stefano Galli", "Roberto Conti", "Davide Mancini",
    "Luca Moretti", "Simone Barbieri", "Gabriele Fontana", "Tommaso Santoro",
    "Giulia Rossi", "Francesca Bianchi", "Chiara Romano", "Valentina Costa",
    "Alessandra Ferrari", "Martina Ricci", "Federica Greco", "Silvia Galli"
]

class SampleDataGenerator:
    """Generator for archaeological sample data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.site_name = "Sito Archeologico di Esempio"
        self.areas = ["A", "B", "C", "D"]
        
        # Archaeological periods
        self.periods = [
            "Età del Bronzo Antico", "Età del Bronzo Medio", "Età del Bronzo Finale",
            "Età del Ferro I", "Età del Ferro II", "Età Romana Repubblicana",
            "Età Romana Imperiale", "Tardoantico", "Altomedioevo", "Medioevo"
        ]
        
        # US formation types  
        self.formations = ["Naturale", "Antropica", "Mista"]
        self.consistencies = ["Compatta", "Semicompatta", "Sciolsa", "Molto sciolsa"]
        self.colors = ["Marrone", "Marrone scuro", "Grigio", "Grigio scuro", "Nero", "Giallo"]
        
        # Material types
        self.material_types = [
            "Ceramica comune", "Ceramica fine", "Terra sigillata", "Ceramica grezza",
            "Vetro", "Bronzo", "Ferro", "Piombo", "Oro", "Argento",
            "Osso lavorato", "Corno", "Avorio", "Pietra", "Marmo",
            "Legno", "Carbone", "Semi", "Moneta", "Laterizio"
        ]
        
        self.ceramic_bodies = ["Depurato", "Semi-depurato", "Grezzo", "Fine", "Grossolano"]
        self.surface_treatments = ["Verniciato", "Ingobbato", "Dipinto", "Graffito", "Nudo"]
        self.conservation_states = ["Ottimo", "Buono", "Discreto", "Cattivo", "Frammentario"]
    
    def create_site(self):
        """Create the sample archaeological site"""
        print("Creating sample site...")
        
        site_data = {
            'sito': self.site_name,
            'nazione': 'Italia',
            'regione': 'Lazio',
            'comune': 'Roma',
            'provincia': 'RM',
            'definizione_sito': 'Scavo stratigrafico',
            'descrizione': 'Sito archeologico di esempio con stratificazione dal Bronzo al Medioevo. '
                          'Presenta evidenze di continuità insediativa con fasi di abbandono e rioccupazione. '
                          'Documentata presenza di strutture abitative, produttive e rituali.',
            'find_check': True
        }
        
        # Create site and commit immediately
        try:
            with self.db_manager.connection.get_session() as session:
                site = Site(**site_data)
                session.add(site)
                session.commit()
                # Access attributes while session is still active
                site_id = site.id_sito
                site_name = site.sito
                
            print(f"✓ Created site: {site_name}")
            return site_data  # Return data dict instead of SQLAlchemy object
            
        except Exception as e:
            print(f"Error creating site: {e}")
            raise
    
    def create_periods(self):
        """Create archaeological periods"""
        print("Creating archaeological periods...")
        
        period_data = [
            ("Età del Bronzo Antico", -2300, -1700, "Sistema cronologico tradizionale"),
            ("Età del Bronzo Medio", -1700, -1350, "Sistema cronologico tradizionale"),
            ("Età del Bronzo Finale", -1350, -950, "Sistema cronologico tradizionale"),
            ("Età del Ferro I", -950, -730, "Sistema cronologico tradizionale"),
            ("Età del Ferro II", -730, -580, "Sistema cronologico tradizionale"),
            ("Età Romana Repubblicana", -509, -27, "Sistema cronologico storico"),
            ("Età Romana Imperiale", -27, 476, "Sistema cronologico storico"),
            ("Tardoantico", 284, 568, "Sistema cronologico storico"),
            ("Altomedioevo", 568, 1000, "Sistema cronologico storico"),
            ("Medioevo", 1000, 1492, "Sistema cronologico storico")
        ]
        
        periods = []
        for name, start, end, chronology in period_data:
            period_data_dict = {
                'period_name': name,
                'start_date': start,
                'end_date': end,
                'chronology': chronology,
                'description': f"Periodo archeologico {name} ({start}-{end})"
            }
            
            with self.db_manager.connection.get_session() as session:
                period = Period(**period_data_dict)
                session.add(period)
                session.commit()
                
            periods.append(period_data_dict)
            
        print(f"✓ Created {len(periods)} periods")
        return periods
    
    def create_thesaurus(self):
        """Create thesaurus entries"""
        print("Creating thesaurus entries...")
        
        count = 0
        for table_name, fields in THESAURUS_MAPPINGS.items():
            for field_name, values in fields.items():
                for value in values:
                    # Create ThesaurusSigle entry
                    with self.db_manager.connection.get_session() as session:
                        sigle = ThesaurusSigle(
                            nome_tabella=table_name,
                            sigla=value,
                            sigla_estesa=value,
                            descrizione=f"Voce controllata per {field_name}: {value}",
                            tipologia_sigla=field_name,
                            lingua='it'
                        )
                        session.add(sigle)
                        
                        # Create ThesaurusField entry
                        field = ThesaurusField(
                            table_name=table_name,
                            field_name=field_name,
                            value=value,
                            label=value,
                            description=f"Valore per campo {field_name}",
                            language='it',
                            active='1',
                            sort_order=count
                        )
                        session.add(field)
                        session.commit()
                        
                    count += 1
                    
        print(f"✓ Created {count} thesaurus entries")
    
    def create_us_records(self, site):
        """Create 100 US records with realistic stratigraphic data"""
        print("Creating 100 US records...")
        
        us_records = []
        
        for us_num in range(1, 101):
            area = random.choice(self.areas)
            
            # Generate realistic descriptions
            if us_num <= 10:
                # Surface layers
                d_strat = f"Strato superficiale di humus con materiale sporadico"
                d_interp = f"Livello di calpestio moderno e accumulo superficiale"
                formation = "Mista"
                period = random.choice(self.periods[-3:])  # Recent periods
            elif us_num <= 30:
                # Medieval layers
                d_strat = f"Strato di terra marrone con inclusi ceramici medievali"
                d_interp = f"Deposito di scarico domestico medievale"
                formation = "Antropica"
                period = random.choice(self.periods[-4:-1])
            elif us_num <= 60:
                # Roman layers
                d_strat = f"Strato compatto con materiali romani e frammenti laterizi"
                d_interp = f"Livello di frequentazione romana con crolli strutturali"
                formation = "Antropica" 
                period = random.choice(self.periods[-7:-4])
            elif us_num <= 85:
                # Iron Age layers
                d_strat = f"Deposito scuro con ceramica protostorica e resti combusti"
                d_interp = f"Livello di vita dell'età del ferro con tracce di combustione"
                formation = "Antropica"
                period = random.choice(self.periods[-9:-7])
            else:
                # Bronze Age layers
                d_strat = f"Strato sterile argilloso con sporadici materiali preistorici"
                d_interp = f"Deposito naturale con tracce di frequentazione bronzea"
                formation = "Naturale"
                period = random.choice(self.periods[:3])
            
            us_data = {
                'sito': site.sito,
                'area': area,
                'us': us_num,
                'd_stratigrafica': d_strat,
                'd_interpretativa': d_interp,
                'descrizione': f"US {us_num} - {d_strat}",
                'interpretazione': d_interp,
                'periodo_iniziale': period,
                'periodo_finale': period,
                'formazione': formation,
                'stato_di_conservazione': random.choice(["Buono", "Discreto", "Cattivo"]),
                'colore': random.choice(self.colors),
                'consistenza': random.choice(self.consistencies),
                'struttura': random.choice(["Stratificata", "Massiva", "Granulare", "Compatta"]),
                'scavato': "Si",
                'attivita': random.choice(["Scavo", "Pulitura", "Sezione"]),
                'anno_scavo': random.randint(2020, 2024),
                'metodo_di_scavo': random.choice(["Stratigrafico", "Meccanico", "Misto"]),
                'data_schedatura': date.today(),
                'schedatore': random.choice(ITALIAN_NAMES),
                'quota_relativa': round(random.uniform(-5.0, 0.0), 2),
                'quota_abs': round(random.uniform(45.0, 50.0), 2),
                'lunghezza_max': round(random.uniform(0.5, 5.0), 2),
                'larghezza_media': round(random.uniform(0.3, 3.0), 2),
                'profondita_max': round(random.uniform(0.1, 1.5), 2),
                'osservazioni': f"US {us_num} - Note di scavo area {area}",
                'datazione': period,
                'direttore_us': random.choice(ITALIAN_NAMES),
                'responsabile_us': random.choice(ITALIAN_NAMES),
                'affidabilita': random.choice(["1", "2", "3"])
            }
            
            us_record = self.db_manager.create(US, us_data)
            us_records.append(us_record)
            
            if us_num % 20 == 0:
                print(f"  Created {us_num} US records...")
        
        print(f"✓ Created {len(us_records)} US records")
        return us_records
    
    def create_stratigraphic_relationships(self, us_records):
        """Create realistic stratigraphic relationships"""
        print("Creating stratigraphic relationships...")
        
        relationships = []
        
        # Create sequential relationships (earlier US above later US)
        for i in range(len(us_records) - 1):
            us_above = us_records[i]
            us_below = us_records[i + 1]
            
            # Skip some relationships to create more realistic matrix
            if random.random() < 0.7:  # 70% chance of relationship
                rel_type = random.choice(["sopra", "copre", "taglia"])
                certainty = random.choice(["certa", "probabile", "dubbia"])
                
                # Create Harris Matrix entry
                matrix_data = {
                    'sito': us_above.sito,
                    'area': us_above.area,
                    'us_sopra': us_above.us,
                    'us_sotto': us_below.us,
                    'tipo_rapporto': rel_type
                }
                matrix_rel = self.db_manager.create(HarrisMatrix, matrix_data)
                
                # Create detailed relationship
                rel_data = {
                    'sito': us_above.sito,
                    'us_from': us_above.us,
                    'us_to': us_below.us,
                    'relationship_type': rel_type,
                    'certainty': certainty,
                    'description': f"US {us_above.us} {rel_type} US {us_below.us} - {certainty}"
                }
                detailed_rel = self.db_manager.create(USRelationships, rel_data)
                
                relationships.append((matrix_rel, detailed_rel))
        
        # Add some cross-cutting relationships
        for _ in range(10):
            us1 = random.choice(us_records[:50])  # Earlier US
            us2 = random.choice(us_records[50:])  # Later US
            
            rel_data = {
                'sito': us1.sito,
                'us_from': us1.us,
                'us_to': us2.us,
                'relationship_type': "taglia",
                'certainty': "probabile",
                'description': f"US {us1.us} taglia US {us2.us} - relazione di taglio"
            }
            cross_rel = self.db_manager.create(USRelationships, rel_data)
            relationships.append((None, cross_rel))
        
        print(f"✓ Created {len(relationships)} stratigraphic relationships")
        return relationships
    
    def create_materials(self, us_records):
        """Create 50 material records distributed across US"""
        print("Creating 50 material records...")
        
        materials = []
        
        for inv_num in range(1, 51):
            # Select random US for material context
            us_context = random.choice(us_records)
            material_type = random.choice(self.material_types)
            
            # Generate realistic data based on material type
            if "Ceramica" in material_type:
                corpo_ceramico = random.choice(self.ceramic_bodies)
                rivestimento = random.choice(self.surface_treatments)
                peso = round(random.uniform(5.0, 500.0), 1)
                diametro = round(random.uniform(8.0, 35.0), 1) if random.random() < 0.3 else None
                eve_orlo = round(random.uniform(0.05, 0.25), 3) if diametro else None
            else:
                corpo_ceramico = None
                rivestimento = None
                peso = round(random.uniform(1.0, 200.0), 1)
                diametro = None
                eve_orlo = None
            
            material_data = {
                'sito': us_context.sito,
                'numero_inventario': inv_num,
                'tipo_reperto': material_type,
                'criterio_schedatura': "Tipo-cronologico",
                'definizione': f"{material_type} - frammento",
                'descrizione': f"Reperto {inv_num}: {material_type} da US {us_context.us}. " +
                              f"Frammento di {material_type.lower()} rinvenuto durante lo scavo stratigrafico. " +
                              f"Presenta caratteristiche tipiche del periodo {us_context.periodo_iniziale}.",
                'area': us_context.area,
                'us': str(us_context.us),
                'lavato': random.choice(["Si", "No"]),
                'nr_cassa': f"C{random.randint(1, 20)}",
                'luogo_conservazione': "Deposito archeologico",
                'stato_conservazione': random.choice(self.conservation_states),
                'datazione_reperto': us_context.periodo_iniziale,
                'peso': peso,
                'corpo_ceramico': corpo_ceramico,
                'rivestimento': rivestimento,
                'diametro_orlo': diametro,
                'eve_orlo': eve_orlo,
                'repertato': random.choice(["Si", "No"]),
                'diagnostico': random.choice(["Si", "No"]),
                'n_reperto': inv_num,
                'tipo_contenitore': random.choice(["Ceramico", "Plastico", "Tessile"]),
                'years': us_context.anno_scavo,
                'schedatore': random.choice(ITALIAN_NAMES),
                'date_scheda': str(date.today()),
                'totale_frammenti': random.randint(1, 15),
                'forme_minime': 1,
                'forme_massime': random.randint(1, 3)
            }
            
            material = self.db_manager.create(InventarioMateriali, material_data)
            materials.append(material)
            
            if inv_num % 10 == 0:
                print(f"  Created {inv_num} materials...")
        
        print(f"✓ Created {len(materials)} material records")
        return materials
    
    def create_periodization(self, us_records, periods):
        """Create periodization assignments for US"""
        print("Creating periodization assignments...")
        
        periodizations = []
        
        # Assign periods to some US records
        for us_record in random.sample(us_records, 30):  # 30% of US
            period = random.choice(periods)
            
            periodization_data = {
                'sito': us_record.sito,
                'area': us_record.area,
                'us': us_record.us,
                'periodo_iniziale': period.period_name,
                'periodo_finale': period.period_name,
                'datazione_estesa': f"Attribuzione cronologica a {period.period_name} "
                                   f"({period.start_date}-{period.end_date})",
                'motivazione': f"Attribuzione basata su materiali ceramici e contesto stratigrafico",
                'period_id_initial': period.id_period,
                'period_id_final': period.id_period,
                'cultura': f"Cultura di {period.period_name}",
                'affidabilita': random.choice(["alta", "media", "bassa"]),
                'note': f"Periodizzazione US {us_record.us} - Area {us_record.area}"
            }
            
            periodization = self.db_manager.create(Periodizzazione, periodization_data)
            periodizations.append(periodization)
        
        print(f"✓ Created {len(periodizations)} periodization assignments")
        return periodizations
    
    def generate_all_data(self):
        """Generate complete sample dataset"""
        print("=" * 60)
        print("GENERATING ARCHAEOLOGICAL SAMPLE DATA")
        print("=" * 60)
        
        try:
            # Create core data
            site = self.create_site()
            periods = self.create_periods()
            self.create_thesaurus()
            
            # Create archaeological records
            us_records = self.create_us_records(site)
            relationships = self.create_stratigraphic_relationships(us_records)
            materials = self.create_materials(us_records)
            periodizations = self.create_periodization(us_records, periods)
            
            print("\n" + "=" * 60)
            print("SAMPLE DATA GENERATION COMPLETED")
            print("=" * 60)
            print(f"✓ Site: {site.sito}")
            print(f"✓ US Records: {len(us_records)}")
            print(f"✓ Relationships: {len(relationships)}")
            print(f"✓ Materials: {len(materials)}")
            print(f"✓ Periods: {len(periods)}")
            print(f"✓ Periodizations: {len(periodizations)}")
            print(f"✓ Thesaurus entries: Complete")
            print("\nDatabase populated successfully!")
            
            return {
                'site': site,
                'us_records': us_records,
                'relationships': relationships,
                'materials': materials,
                'periods': periods,
                'periodizations': periodizations
            }
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise

def main():
    """Main function to run sample data generation"""
    
    # Initialize database connection with SQLite
    from pyarchinit_mini.database.connection import DatabaseConnection
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'data', 'pyarchinit_mini_sample.db')
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db_connection = DatabaseConnection.sqlite(db_path)
    db_manager = DatabaseManager(db_connection)
    
    try:
        # Initialize database schema
        print("Initializing database schema...")
        db_connection.create_tables()
        print("✓ Database schema initialized")
        
        # Generate sample data
        generator = SampleDataGenerator(db_manager)
        data = generator.generate_all_data()
        
        print(f"\nSample data generated successfully!")
        print(f"You can now test the application with:")
        print(f"- Site: {data['site'].sito}")
        print(f"- {len(data['us_records'])} US records")
        print(f"- {len(data['materials'])} material records")
        print(f"- Complete stratigraphic relationships")
        print(f"- Full thesaurus vocabularies")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())