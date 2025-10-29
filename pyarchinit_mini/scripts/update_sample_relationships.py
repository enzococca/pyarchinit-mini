#!/usr/bin/env python3
"""
Script per aggiornare il database di esempio con relazioni stratigrafiche corrette
Sostituisce le relazioni generiche "sopra" con relazioni specifiche PyArchInit
"""

import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

def update_sample_relationships():
    """Aggiorna le relazioni nel database di esempio"""
    
    print("🔄 Aggiornamento relazioni stratigrafiche nel database di esempio")
    print("=" * 70)
    
    # Connessione al database
    db_path = 'data/pyarchinit_mini_sample.db'
    connection = DatabaseConnection(f'sqlite:///{db_path}')
    db_manager = DatabaseManager(connection)
    
    # Relazioni stratigrafiche corrette da usare
    correct_relationships = [
        # Relazioni sequenziali (normale stratigrafia)
        "['Copre', 'US_{}']",
        "['Coperto da', 'US_{}']", 
        "['Riempie', 'US_{}']",
        "['Riempito da', 'US_{}']",
        "['Si appoggia a', 'US_{}']",
        "['Gli si appoggia', 'US_{}']",
        
        # Relazioni negative (tagli)
        "['Taglia', 'US_{}']",
        "['Tagliato da', 'US_{}']",
        
        # Relazioni contemporanee
        "['Uguale a', 'US_{}']",
        "['Si lega a', 'US_{}']"
    ]
    
    try:
        with connection.get_session() as session:
            from sqlalchemy import text
            # Query per ottenere tutte le US
            result = session.execute(text("SELECT id_us, us, sito, area FROM us_table ORDER BY us"))
            us_records = result.fetchall()
            
            print(f"📊 Trovate {len(us_records)} US da aggiornare")
            
            updated_count = 0
            
            for i, record in enumerate(us_records):
                id_us, us_num, sito, area = record
                
                # Genera relazioni realistiche
                relationships = []
                
                # Ogni US ha 1-3 relazioni con US adiacenti
                num_relations = random.randint(1, 3)
                
                for _ in range(num_relations):
                    # Scegli una relazione casuale
                    rel_template = random.choice(correct_relationships)
                    
                    # Trova US correlata (precedente o successiva)
                    if i > 0 and random.random() > 0.5:
                        # Relazione con US precedente
                        related_us = us_records[i-1][1]  # us number
                    elif i < len(us_records) - 1:
                        # Relazione con US successiva  
                        related_us = us_records[i+1][1]  # us number
                    else:
                        # Fallback: usa US casuale
                        related_record = random.choice(us_records)
                        related_us = related_record[1]
                    
                    # Crea relazione con formato corretto
                    relationship = rel_template.format(related_us)
                    relationships.append(relationship)
                
                # Converti in formato lista Python come stringa
                rapporti_str = str(relationships)
                
                # Aggiorna il record
                update_query = text("""
                UPDATE us_table 
                SET rapporti = :rapporti 
                WHERE id_us = :id_us
                """)
                session.execute(update_query, {"rapporti": rapporti_str, "id_us": id_us})
                updated_count += 1
                
                if updated_count % 20 == 0:
                    print(f"   ✅ Aggiornate {updated_count} US...")
            
            # Commit delle modifiche
            session.commit()
            
            print(f"\n✅ Aggiornamento completato!")
            print(f"   📝 {updated_count} US aggiornate con relazioni corrette")
            print(f"   💾 Modifiche salvate in {db_path}")
            
            # Verifica alcune relazioni aggiornate
            print(f"\n🔍 Verifica delle relazioni aggiornate:")
            verification_query = text("SELECT us, rapporti FROM us_table WHERE rapporti IS NOT NULL LIMIT 5")
            result = session.execute(verification_query)
            
            for us_num, rapporti in result.fetchall():
                print(f"   US {us_num}: {rapporti}")
                
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("Questo script aggiornerà le relazioni stratigrafiche nel database di esempio")
    print("Sostituirà le relazioni generiche con relazioni specifiche PyArchInit")
    print("")
    
    response = input("Continuare? (s/n): ")
    if response.lower() in ['s', 'si', 'y', 'yes']:
        update_sample_relationships()
        
        print("\n🔄 Copiare il database aggiornato come database principale:")
        print("   python scripts/load_sample_as_main.py")
    else:
        print("Operazione annullata.")

if __name__ == "__main__":
    main()