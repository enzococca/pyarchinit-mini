"""
Script per normalizzare le relazioni stratigrafiche nel database.
Migra i dati dal campo testuale 'rapporti' nella tabella strutturata 'us_relationships_table'.
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path


def parse_relationships(rapporti_text):
    """
    Parsifica il campo rapporti testuale e estrae le relazioni.

    Input: "Copre 1002, taglia 1005"
    Output: [("Copre", 1002), ("taglia", 1005)]
    """
    if not rapporti_text or rapporti_text.strip() == "":
        return []

    relationships = []

    # Pattern per trovare: "tipo_relazione numero_us"
    # Supporta vari formati come "Copre 1002", "Si appoggia a 1001", "Taglia 1005"
    pattern = r'([A-Za-z\s]+?)\s+(\d+)'

    matches = re.findall(pattern, rapporti_text)

    for rel_type, us_number in matches:
        rel_type = rel_type.strip().capitalize()  # Normalizza: "copre" -> "Copre"
        relationships.append((rel_type, int(us_number)))

    return relationships


def migrate_relationships(db_path):
    """
    Migra le relazioni dal campo testuale alla tabella strutturata.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Pulisci la tabella delle relazioni se esiste già
        print("Pulizia tabella us_relationships_table...")
        cursor.execute("DELETE FROM us_relationships_table")

        # Ottieni tutte le US con relazioni
        print("Lettura relazioni esistenti...")
        cursor.execute("""
            SELECT id_us, sito, us, rapporti
            FROM us_table
            WHERE rapporti IS NOT NULL AND rapporti != ''
        """)

        us_records = cursor.fetchall()
        print(f"Trovate {len(us_records)} US con relazioni")

        # Contatori per statistiche
        total_relationships = 0
        skipped = 0

        # Per ogni US, parsifica le relazioni e inseriscile nella tabella strutturata
        for id_us, sito, us_from, rapporti in us_records:
            relationships = parse_relationships(rapporti)

            if not relationships:
                print(f"  Attenzione: nessuna relazione parsata per US {us_from}: {rapporti}")
                skipped += 1
                continue

            for rel_type, us_to in relationships:
                cursor.execute("""
                    INSERT INTO us_relationships_table
                    (sito, us_from, us_to, relationship_type, certainty, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sito,
                    us_from,
                    us_to,
                    rel_type,
                    'Certa',  # Default certainty
                    datetime.now(),
                    datetime.now()
                ))
                total_relationships += 1

        # Commit delle modifiche
        conn.commit()

        print(f"\nMigrazione completata con successo!")
        print(f"  - US processate: {len(us_records)}")
        print(f"  - Relazioni create: {total_relationships}")
        print(f"  - US saltate (parsing fallito): {skipped}")

        # Mostra alcuni esempi
        print("\nEsempi di relazioni create:")
        cursor.execute("""
            SELECT us_from, relationship_type, us_to
            FROM us_relationships_table
            LIMIT 10
        """)

        for us_from, rel_type, us_to in cursor.fetchall():
            print(f"  US {us_from} -> {rel_type} -> US {us_to}")

    except Exception as e:
        conn.rollback()
        print(f"Errore durante la migrazione: {e}")
        raise

    finally:
        conn.close()


def verify_migration(db_path):
    """
    Verifica la migrazione confrontando i dati.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n=== Verifica migrazione ===")

        # Conta le relazioni nella tabella strutturata
        cursor.execute("SELECT COUNT(*) FROM us_relationships_table")
        count = cursor.fetchone()[0]
        print(f"Relazioni nella tabella strutturata: {count}")

        # Raggruppa per tipo di relazione
        cursor.execute("""
            SELECT relationship_type, COUNT(*)
            FROM us_relationships_table
            GROUP BY relationship_type
            ORDER BY COUNT(*) DESC
        """)

        print("\nDistribuzione per tipo di relazione:")
        for rel_type, count in cursor.fetchall():
            print(f"  {rel_type}: {count}")

    finally:
        conn.close()


if __name__ == "__main__":
    # Path al database
    db_path = Path(__file__).parent.parent / "data" / "pyarchinit_mini_sample.db"

    if not db_path.exists():
        print(f"Errore: database non trovato in {db_path}")
        exit(1)

    print(f"Migrazione relazioni per database: {db_path}")
    print("=" * 60)

    # Esegui la migrazione
    migrate_relationships(str(db_path))

    # Verifica il risultato
    verify_migration(str(db_path))

    print("\n✓ Migrazione completata!")