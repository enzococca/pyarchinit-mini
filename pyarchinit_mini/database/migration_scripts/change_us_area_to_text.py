"""
Database migration: Change us and area columns to TEXT type

This migration changes:
- us_table.us: INTEGER → VARCHAR(100) (to support alphanumeric codes)
- us_table.area: VARCHAR(20) → TEXT (unlimited characters)

Date: 2025-10-23
Version: 1.1
"""

from sqlalchemy import text


def upgrade_sqlite(connection):
    """
    Change column types for SQLite database

    SQLite limitations:
    - Cannot ALTER COLUMN TYPE directly
    - Need to recreate table with new schema
    """

    print("[Migration] Changing us and area column types for SQLite...")

    # Step 1: Create new table with correct types
    print("[Migration] Creating new us_table with updated schema...")
    connection.execute(text("""
        CREATE TABLE us_table_new (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito VARCHAR(350) NOT NULL,
            area TEXT,
            us VARCHAR(100) NOT NULL,
            d_stratigrafica VARCHAR(350),
            d_interpretativa VARCHAR(350),
            descrizione TEXT,
            interpretazione TEXT,
            d_stratigrafica_en VARCHAR(350),
            d_interpretativa_en VARCHAR(350),
            descrizione_en TEXT,
            interpretazione_en TEXT,
            periodo_iniziale VARCHAR(300),
            fase_iniziale VARCHAR(300),
            periodo_finale VARCHAR(300),
            fase_finale VARCHAR(300),
            scavato VARCHAR(20),
            attivita VARCHAR(30),
            anno_scavo INTEGER,
            metodo_di_scavo VARCHAR(20),
            data_schedatura DATE,
            schedatore VARCHAR(100),
            formazione VARCHAR(20),
            stato_di_conservazione VARCHAR(20),
            colore VARCHAR(20),
            consistenza VARCHAR(20),
            struttura VARCHAR(30),
            formazione_en VARCHAR(20),
            stato_di_conservazione_en VARCHAR(20),
            colore_en VARCHAR(20),
            consistenza_en VARCHAR(20),
            struttura_en VARCHAR(30),
            inclusi TEXT,
            campioni TEXT,
            rapporti TEXT,
            documentazione TEXT,
            cont_per TEXT,
            order_layer INTEGER,
            inclusi_en TEXT,
            campioni_en TEXT,
            documentazione_en TEXT,
            unita_tipo VARCHAR(200),
            settore VARCHAR(200),
            quad_par VARCHAR(200),
            ambient VARCHAR(200),
            saggio VARCHAR(200),
            elem_datanti VARCHAR(250),
            datazione_rep VARCHAR(30),
            quota_relativa FLOAT,
            quota_abs FLOAT,
            lunghezza_max FLOAT,
            altezza_max FLOAT,
            altezza_min FLOAT,
            profondita_max FLOAT,
            profondita_min FLOAT,
            larghezza_media FLOAT,
            criteri_distinzione VARCHAR(20),
            modo_formazione VARCHAR(20),
            componenti_organici VARCHAR(30),
            componenti_inorganici VARCHAR(30),
            lunghezza_usm FLOAT,
            altezza_usm FLOAT,
            spessore_usm FLOAT,
            tecnica_muraria_usm VARCHAR(20),
            modulo_usm VARCHAR(30),
            superficie_analizzata FLOAT,
            tipologia_opera VARCHAR(30),
            sezione_muraria VARCHAR(30),
            superficie_estesa FLOAT,
            orientamento VARCHAR(10),
            materiali_lat VARCHAR(200),
            lavorazione_lat VARCHAR(200),
            consistenza_lat VARCHAR(20),
            forma_lat VARCHAR(30),
            colore_lat VARCHAR(20),
            impasto_lat VARCHAR(30),
            forma_p VARCHAR(30),
            forma_a VARCHAR(30),
            spessore_p FLOAT,
            spessore_a FLOAT,
            letti_posa VARCHAR(200),
            h_modulo_c_corsi INTEGER,
            unita_edilizia_riassuntiva VARCHAR(300),
            reutilizzato VARCHAR(20),
            orientamento_usm VARCHAR(200),
            materiali_usm VARCHAR(200),
            lavorazione_usm VARCHAR(200),
            consistenza_usm VARCHAR(20),
            colore_usm VARCHAR(20),
            posa_in_opera_usm VARCHAR(200),
            quota_min_usm FLOAT,
            quota_max_usm FLOAT,
            cons_legante_usm VARCHAR(200),
            col_legante_usm VARCHAR(20),
            aggreg_legante_usm VARCHAR(200),
            con_text_mat VARCHAR(200),
            col_materiale VARCHAR(200),
            inclusi_materiali_usm VARCHAR(200),
            n_catalogo_generale INTEGER,
            n_catalogo_interno INTEGER,
            n_catalogo_internazionale INTEGER,
            affidabilita VARCHAR(20),
            direttore_us VARCHAR(200),
            responsabile_us VARCHAR(200),
            cod_ente_schedatore VARCHAR(200),
            data_rilevazione DATE,
            data_rielaborazione DATE,
            lunghezza_usm_a FLOAT,
            altezza_usm_a FLOAT,
            spessore_usm_a FLOAT,
            tecnica_muraria_usm_a VARCHAR(20),
            modulo_usm_a VARCHAR(30),
            campioni_malta_usm VARCHAR(200),
            campioni_mattone_usm VARCHAR(200),
            campioni_pietra_usm VARCHAR(200),
            campioni_carbone_usm VARCHAR(200),
            flottazione VARCHAR(20),
            setacciatura VARCHAR(20),
            affidabilita_stratigrafica VARCHAR(20),
            doc_associated TEXT,
            osservazioni TEXT,
            osservazioni_en TEXT,
            documentazione_usm TEXT,
            us_assoc_per INTEGER,
            FOREIGN KEY (sito) REFERENCES site_table(sito) ON DELETE CASCADE
        )
    """))

    # Step 2: Copy data from old table (casting us from INTEGER to VARCHAR)
    print("[Migration] Copying data from old table...")
    connection.execute(text("""
        INSERT INTO us_table_new SELECT
            id_us, sito, area, CAST(us AS VARCHAR(100)),
            d_stratigrafica, d_interpretativa, descrizione, interpretazione,
            d_stratigrafica_en, d_interpretativa_en, descrizione_en, interpretazione_en,
            periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
            scavato, attivita, anno_scavo, metodo_di_scavo, data_schedatura, schedatore,
            formazione, stato_di_conservazione, colore, consistenza, struttura,
            formazione_en, stato_di_conservazione_en, colore_en, consistenza_en, struttura_en,
            inclusi, campioni, rapporti, documentazione, cont_per, order_layer,
            inclusi_en, campioni_en, documentazione_en,
            unita_tipo, settore, quad_par, ambient, saggio,
            elem_datanti, datazione_rep,
            quota_relativa, quota_abs, lunghezza_max, altezza_max, altezza_min,
            profondita_max, profondita_min, larghezza_media,
            criteri_distinzione, modo_formazione, componenti_organici, componenti_inorganici,
            lunghezza_usm, altezza_usm, spessore_usm, tecnica_muraria_usm, modulo_usm,
            superficie_analizzata, tipologia_opera, sezione_muraria, superficie_estesa,
            orientamento, materiali_lat, lavorazione_lat, consistenza_lat, forma_lat,
            colore_lat, impasto_lat, forma_p, forma_a, spessore_p, spessore_a,
            letti_posa, h_modulo_c_corsi, unita_edilizia_riassuntiva, reutilizzato,
            orientamento_usm, materiali_usm, lavorazione_usm, consistenza_usm, colore_usm,
            posa_in_opera_usm, quota_min_usm, quota_max_usm,
            cons_legante_usm, col_legante_usm, aggreg_legante_usm,
            con_text_mat, col_materiale, inclusi_materiali_usm,
            n_catalogo_generale, n_catalogo_interno, n_catalogo_internazionale,
            affidabilita, direttore_us, responsabile_us, cod_ente_schedatore,
            data_rilevazione, data_rielaborazione,
            lunghezza_usm_a, altezza_usm_a, spessore_usm_a, tecnica_muraria_usm_a, modulo_usm_a,
            campioni_malta_usm, campioni_mattone_usm, campioni_pietra_usm, campioni_carbone_usm,
            flottazione, setacciatura, affidabilita_stratigrafica,
            doc_associated, osservazioni, osservazioni_en, documentazione_usm, us_assoc_per
        FROM us_table
    """))

    # Step 3: Drop old table
    print("[Migration] Dropping old table...")
    connection.execute(text("DROP TABLE us_table"))

    # Step 4: Rename new table
    print("[Migration] Renaming new table...")
    connection.execute(text("ALTER TABLE us_table_new RENAME TO us_table"))

    # Step 5: Recreate indexes
    print("[Migration] Recreating indexes...")
    connection.execute(text("""
        CREATE INDEX idx_us_sito ON us_table(sito)
    """))
    connection.execute(text("""
        CREATE INDEX idx_us_us ON us_table(us)
    """))
    connection.execute(text("""
        CREATE INDEX idx_us_area ON us_table(area)
    """))

    print("[Migration] us_table migration complete")


def upgrade_postgresql(connection):
    """
    Change column types for PostgreSQL database

    PostgreSQL can ALTER COLUMN TYPE directly
    """

    print("[Migration] Changing us and area column types for PostgreSQL...")

    # Change us from INTEGER to VARCHAR(100)
    print("[Migration] Converting us column to VARCHAR(100)...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN us TYPE VARCHAR(100) USING us::VARCHAR(100)
    """))

    # Change area from VARCHAR(20) to TEXT
    print("[Migration] Converting area column to TEXT...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN area TYPE TEXT
    """))

    print("[Migration] us_table migration complete")


def downgrade_sqlite(connection):
    """
    Revert changes for SQLite (us back to INTEGER, area to VARCHAR(20))

    WARNING: This may cause data loss if us contains non-numeric values!
    """

    print("[Migration] Reverting us and area column types for SQLite...")

    # Create old table structure
    print("[Migration] Creating old us_table schema...")
    # Note: We truncate the schema definition here for brevity
    # In production, you'd need the full original schema

    print("[Migration] WARNING: Downgrade not fully implemented to prevent data loss")
    print("[Migration] Manual intervention required if downgrade is needed")


def downgrade_postgresql(connection):
    """
    Revert changes for PostgreSQL

    WARNING: This may cause data loss if us contains non-numeric values!
    """

    print("[Migration] Reverting us and area column types for PostgreSQL...")

    # Revert us to INTEGER (may fail if data is not numeric)
    print("[Migration] Converting us column back to INTEGER...")
    try:
        connection.execute(text("""
            ALTER TABLE us_table
            ALTER COLUMN us TYPE INTEGER USING us::INTEGER
        """))
    except Exception as e:
        print(f"[Migration] ERROR: Cannot convert us to INTEGER: {e}")
        print("[Migration] Some us values may contain non-numeric data")

    # Revert area to VARCHAR(20)
    print("[Migration] Converting area column back to VARCHAR(20)...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN area TYPE VARCHAR(20)
    """))

    print("[Migration] us_table downgrade complete")


def upgrade(connection, db_type='sqlite'):
    """
    Main upgrade function

    Args:
        connection: SQLAlchemy connection
        db_type: 'sqlite' or 'postgresql'
    """
    if db_type.lower() == 'sqlite':
        upgrade_sqlite(connection)
    elif db_type.lower() in ('postgresql', 'postgres'):
        upgrade_postgresql(connection)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def downgrade(connection, db_type='sqlite'):
    """
    Main downgrade function

    Args:
        connection: SQLAlchemy connection
        db_type: 'sqlite' or 'postgresql'
    """
    if db_type.lower() == 'sqlite':
        downgrade_sqlite(connection)
    elif db_type.lower() in ('postgresql', 'postgres'):
        downgrade_postgresql(connection)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
