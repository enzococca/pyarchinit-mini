"""
Database migrations for PyArchInit-Mini
"""

import logging
from sqlalchemy import text, inspect
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseMigrations:
    """
    Handle database schema migrations
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection = db_manager.connection
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        try:
            inspector = inspect(self.connection.engine)
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
        except Exception as e:
            logger.error(f"Error checking column {column_name} in table {table_name}: {e}")
            return False
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value: str = None):
        """Add a column to a table if it doesn't exist"""
        try:
            if not self.check_column_exists(table_name, column_name):
                with self.connection.get_session() as session:
                    # Build ALTER TABLE statement
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    if default_value is not None:
                        alter_sql += f" DEFAULT {default_value}"
                    
                    session.execute(text(alter_sql))
                    session.commit()
                    logger.info(f"Added column {column_name} to table {table_name}")
                    return True
            else:
                logger.info(f"Column {column_name} already exists in table {table_name}")
                return False
        except Exception as e:
            logger.error(f"Error adding column {column_name} to table {table_name}: {e}")
            raise
    
    def migrate_inventario_materiali_table(self):
        """Migrate inventario_materiali_table to include all new fields"""
        try:
            logger.info("Starting migration for inventario_materiali_table...")
            
            # List of new columns to add
            new_columns = [
                ('schedatore', 'TEXT'),
                ('date_scheda', 'TEXT'),
                ('punto_rinv', 'TEXT'),
                ('negativo_photo', 'TEXT'),
                ('diapositiva', 'TEXT')
            ]
            
            migrations_applied = 0
            
            for column_name, column_type in new_columns:
                if self.add_column_if_not_exists('inventario_materiali_table', column_name, column_type):
                    migrations_applied += 1
            
            logger.info(f"Migration completed. {migrations_applied} new columns added to inventario_materiali_table")
            return migrations_applied
            
        except Exception as e:
            logger.error(f"Error during inventario_materiali_table migration: {e}")
            raise
    
    def migrate_i18n_columns(self):
        """Add i18n columns (_en) for translatable fields"""
        try:
            logger.info("Starting i18n column migrations...")
            
            migrations_applied = 0
            
            # Site table i18n columns
            site_columns = [
                ('definizione_sito_en', 'VARCHAR(250)'),
                ('descrizione_en', 'TEXT')
            ]
            
            for column_name, column_type in site_columns:
                if self.add_column_if_not_exists('site_table', column_name, column_type):
                    migrations_applied += 1
            
            # US table i18n columns
            us_text_columns = [
                ('descrizione_en', 'TEXT'),
                ('interpretazione_en', 'TEXT'),
                ('inclusi_en', 'TEXT'),
                ('campioni_en', 'TEXT'),
                ('documentazione_en', 'TEXT'),
                ('osservazioni_en', 'TEXT')
            ]
            
            us_varchar_columns = [
                ('d_stratigrafica_en', 'VARCHAR(350)'),
                ('d_interpretativa_en', 'VARCHAR(350)'),
                ('formazione_en', 'VARCHAR(20)'),
                ('stato_di_conservazione_en', 'VARCHAR(20)'),
                ('colore_en', 'VARCHAR(20)'),
                ('consistenza_en', 'VARCHAR(20)'),
                ('struttura_en', 'VARCHAR(30)')
            ]
            
            for column_name, column_type in us_text_columns + us_varchar_columns:
                if self.add_column_if_not_exists('us_table', column_name, column_type):
                    migrations_applied += 1
            
            # Inventario materiali table i18n columns
            inv_text_columns = [
                ('tipo_reperto_en', 'TEXT'),
                ('criterio_schedatura_en', 'TEXT'),
                ('definizione_en', 'TEXT'),
                ('descrizione_en', 'TEXT'),
                ('elementi_reperto_en', 'TEXT')
            ]
            
            inv_varchar_columns = [
                ('stato_conservazione_en', 'VARCHAR(200)'),
                ('corpo_ceramico_en', 'VARCHAR(200)'),
                ('rivestimento_en', 'VARCHAR(200)'),
                ('tipo_contenitore_en', 'VARCHAR(200)')
            ]
            
            for column_name, column_type in inv_text_columns + inv_varchar_columns:
                if self.add_column_if_not_exists('inventario_materiali_table', column_name, column_type):
                    migrations_applied += 1
            
            logger.info(f"i18n migration completed. {migrations_applied} new columns added")
            return migrations_applied
            
        except Exception as e:
            logger.error(f"Error during i18n migration: {e}")
            raise
    
    def migrate_tipo_documento(self):
        """Add tipo_documento and file_path columns to US table"""
        try:
            logger.info("Starting tipo_documento migration...")

            migrations_applied = 0

            # Add tipo_documento column
            if self.add_column_if_not_exists('us_table', 'tipo_documento', 'VARCHAR(100)'):
                migrations_applied += 1

            # Add file_path column (for document files)
            if self.add_column_if_not_exists('us_table', 'file_path', 'TEXT'):
                migrations_applied += 1

            logger.info(f"tipo_documento migration completed. {migrations_applied} new columns added")
            return migrations_applied

        except Exception as e:
            logger.error(f"Error during tipo_documento migration: {e}")
            raise

    def migrate_concurrency_columns(self):
        """Add concurrency tracking columns to all main tables."""
        import uuid as uuid_mod
        try:
            logger.info("Starting concurrency columns migration...")
            migrations_applied = 0

            tables = [
                'site_table', 'us_table', 'us_relationships_table',
                'harris_matrix_table', 'period_table', 'datazioni_table',
                'extended_matrix_table',
                'inventario_materiali_table',
                'periodizzazione_table', 'media_table', 'media_thumb_table',
                'documentation_table',
                'pyarchinit_thesaurus_sigle', 'thesaurus_field', 'thesaurus_category',
                'users',
            ]

            concurrency_columns = [
                ('entity_uuid', 'VARCHAR(36)'),
                ('version_number', 'INTEGER', '1'),
                ('last_modified_by', 'VARCHAR(100)'),
                ('last_modified_timestamp', 'TIMESTAMP'),
                ('sync_status', 'VARCHAR(20)', "'new'"),
                ('editing_by', 'VARCHAR(100)'),
                ('editing_since', 'TIMESTAMP'),
            ]

            for table in tables:
                for col_def in concurrency_columns:
                    col_name = col_def[0]
                    col_type = col_def[1]
                    default = col_def[2] if len(col_def) > 2 else None
                    if self.add_column_if_not_exists(table, col_name, col_type, default):
                        migrations_applied += 1

            # Back-fill entity_uuid for existing rows that have NULL
            for table in tables:
                try:
                    with self.connection.get_session() as session:
                        rows = session.execute(
                            text(f"SELECT rowid FROM {table} WHERE entity_uuid IS NULL")
                        ).fetchall()
                        for row in rows:
                            new_uuid = str(uuid_mod.uuid4())
                            session.execute(
                                text(f"UPDATE {table} SET entity_uuid = :uuid WHERE rowid = :rid"),
                                {"uuid": new_uuid, "rid": row[0]}
                            )
                        session.commit()
                except Exception as e:
                    logger.warning(f"UUID backfill for {table}: {e}")

            logger.info(f"Concurrency migration done. {migrations_applied} columns added")
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during concurrency migration: {e}")
            raise

    def migrate_inventario_extra_columns(self):
        """Add missing columns to inventario_materiali_table."""
        try:
            logger.info("Starting inventario extra columns migration...")
            migrations_applied = 0
            extra = [
                ('quota_usm', 'NUMERIC(10,3)'),
                ('unita_misura_quota', 'VARCHAR(20)'),
                ('photo_id', 'TEXT'),
                ('drawing_id', 'TEXT'),
            ]
            for col_name, col_type in extra:
                if self.add_column_if_not_exists('inventario_materiali_table', col_name, col_type):
                    migrations_applied += 1
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during inventario extra migration: {e}")
            raise

    def migrate_us_extra_columns(self):
        """Add all missing pyarchinit US columns to us_table."""
        try:
            logger.info("Starting US extra columns migration...")
            migrations_applied = 0
            columns = [
                ('elem_datanti', 'TEXT'), ('funz_statica', 'TEXT'),
                ('lavorazione', 'TEXT'), ('spess_giunti', 'TEXT'),
                ('letti_posa', 'TEXT'), ('alt_mod', 'TEXT'),
                ('un_ed_riass', 'TEXT'), ('reimp', 'TEXT'),
                ('posa_opera', 'TEXT'),
                ('quota_min_usm', 'NUMERIC(6,2)'), ('quota_max_usm', 'NUMERIC(6,2)'),
                ('cons_legante', 'TEXT'), ('col_legante', 'TEXT'),
                ('aggreg_legante', 'TEXT'), ('con_text_mat', 'TEXT'),
                ('col_materiale', 'TEXT'), ('inclusi_materiali_usm', 'TEXT'),
                ('ref_tm', 'TEXT'), ('ref_ra', 'TEXT'), ('ref_n', 'TEXT'),
                ('posizione', 'TEXT'), ('criteri_distinzione', 'TEXT'),
                ('modo_formazione', 'TEXT'),
                ('componenti_organici', 'TEXT'), ('componenti_inorganici', 'TEXT'),
                ('quota_max_abs', 'NUMERIC(6,2)'), ('quota_max_rel', 'NUMERIC(6,2)'),
                ('quota_min_abs', 'NUMERIC(6,2)'), ('quota_min_rel', 'NUMERIC(6,2)'),
                ('cod_ente_schedatore', 'TEXT'),
                ('data_rilevazione', 'VARCHAR(20)'), ('data_rielaborazione', 'VARCHAR(20)'),
                ('lunghezza_usm', 'NUMERIC(6,2)'), ('altezza_usm', 'NUMERIC(6,2)'),
                ('spessore_usm', 'NUMERIC(6,2)'),
                ('tecnica_muraria_usm', 'TEXT'), ('modulo_usm', 'TEXT'),
                ('campioni_malta_usm', 'TEXT'), ('campioni_mattone_usm', 'TEXT'),
                ('campioni_pietra_usm', 'TEXT'),
                ('provenienza_materiali_usm', 'TEXT'),
                ('criteri_distinzione_usm', 'TEXT'), ('uso_primario_usm', 'TEXT'),
                ('tipologia_opera', 'TEXT'), ('sezione_muraria', 'TEXT'),
                ('superficie_analizzata', 'TEXT'), ('orientamento', 'TEXT'),
                ('materiali_lat', 'TEXT'), ('lavorazione_lat', 'TEXT'),
                ('consistenza_lat', 'TEXT'), ('forma_lat', 'TEXT'),
                ('colore_lat', 'TEXT'), ('impasto_lat', 'TEXT'),
                ('forma_p', 'TEXT'), ('colore_p', 'TEXT'),
                ('taglio_p', 'TEXT'), ('posa_opera_p', 'TEXT'),
                ('inerti_usm', 'TEXT'), ('tipo_legante_usm', 'TEXT'),
                ('rifinitura_usm', 'TEXT'),
                ('materiale_p', 'TEXT'), ('consistenza_p', 'TEXT'),
                ('rapporti2', 'TEXT'), ('doc_usv', 'TEXT'),
            ]
            for col_name, col_type in columns:
                if self.add_column_if_not_exists('us_table', col_name, col_type):
                    migrations_applied += 1
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during US extra migration: {e}")
            raise

    def migrate_us_column_to_text(self):
        """Convert us_table.us from VARCHAR(100) to TEXT (PostgreSQL only — SQLite is dynamic)."""
        try:
            engine = self.connection.engine
            dialect = engine.dialect.name
            if dialect != 'postgresql':
                return 0  # SQLite treats VARCHAR and TEXT identically, no-op

            with self.connection.get_session() as session:
                # Check current type
                result = session.execute(
                    text("""SELECT data_type FROM information_schema.columns
                            WHERE table_name='us_table' AND column_name='us'""")
                ).fetchone()
                if result and result[0].lower() in ('text', 'character varying'):
                    if result[0].lower() == 'text':
                        return 0  # Already TEXT
                    # Convert VARCHAR → TEXT
                    session.execute(text(
                        "ALTER TABLE us_table ALTER COLUMN us TYPE TEXT"
                    ))
                    session.commit()
                    logger.info("Migrated us_table.us: VARCHAR → TEXT")
                    return 1
            return 0
        except Exception as e:
            logger.warning(f"migrate_us_column_to_text: {e}")
            return 0

    def migrate_user_sync_trigger(self):
        """Create bidirectional sync trigger between pyarchinit_users and users tables.
        PostgreSQL only. Maps PyArchInit roles to Mini roles and vice versa."""
        try:
            engine = self.connection.engine
            if engine.dialect.name != 'postgresql':
                return 0

            with self.connection.get_session() as session:
                # Check if pyarchinit_users exists
                exists = session.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = 'pyarchinit_users')"
                )).scalar()
                if not exists:
                    logger.info("pyarchinit_users not found, skipping user sync trigger")
                    return 0

                # Check if trigger already exists
                trigger_exists = session.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_sync_pyarchinit_to_mini_users')"
                )).scalar()
                if trigger_exists:
                    logger.info("User sync triggers already exist")
                    return 0

                # --- PyArchInit → Mini trigger ---
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION sync_pyarchinit_to_mini_users() RETURNS TRIGGER AS $$
                    DECLARE
                        mini_role VARCHAR(10);
                        mini_id INTEGER;
                    BEGIN
                        -- Map PyArchInit role to Mini role
                        CASE LOWER(NEW.role)
                            WHEN 'admin' THEN mini_role := 'ADMIN';
                            WHEN 'responsabile' THEN mini_role := 'ADMIN';
                            WHEN 'archeologo' THEN mini_role := 'OPERATOR';
                            WHEN 'studente' THEN mini_role := 'OPERATOR';
                            WHEN 'guest' THEN mini_role := 'VIEWER';
                            ELSE mini_role := 'VIEWER';
                        END CASE;

                        IF TG_OP = 'INSERT' THEN
                            -- Check if user already exists in Mini
                            SELECT id INTO mini_id FROM users WHERE username = NEW.username;
                            IF mini_id IS NULL THEN
                                INSERT INTO users (username, email, full_name, hashed_password, role, is_active, created_at)
                                VALUES (NEW.username, NEW.email, NEW.full_name,
                                        COALESCE(NEW.password_hash, '!needs_reset'),
                                        mini_role, COALESCE(NEW.is_active, true), NOW());
                            END IF;
                            RETURN NEW;

                        ELSIF TG_OP = 'UPDATE' THEN
                            UPDATE users SET
                                full_name = NEW.full_name,
                                email = NEW.email,
                                role = mini_role,
                                is_active = COALESCE(NEW.is_active, true),
                                updated_at = NOW()
                            WHERE username = NEW.username;
                            -- If password changed, update it too
                            IF NEW.password_hash IS DISTINCT FROM OLD.password_hash THEN
                                UPDATE users SET hashed_password = NEW.password_hash WHERE username = NEW.username;
                            END IF;
                            RETURN NEW;

                        ELSIF TG_OP = 'DELETE' THEN
                            UPDATE users SET is_active = false WHERE username = OLD.username;
                            RETURN OLD;
                        END IF;
                    END;
                    $$ LANGUAGE plpgsql
                """))

                session.execute(text("""
                    CREATE TRIGGER trg_sync_pyarchinit_to_mini_users
                        AFTER INSERT OR UPDATE OR DELETE ON pyarchinit_users
                        FOR EACH ROW EXECUTE FUNCTION sync_pyarchinit_to_mini_users()
                """))

                # --- Mini → PyArchInit trigger ---
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION sync_mini_to_pyarchinit_users() RETURNS TRIGGER AS $$
                    DECLARE
                        pa_role VARCHAR(20);
                        pa_id INTEGER;
                    BEGIN
                        -- Map Mini role to PyArchInit role
                        CASE UPPER(NEW.role)
                            WHEN 'ADMIN' THEN pa_role := 'admin';
                            WHEN 'OPERATOR' THEN pa_role := 'responsabile';
                            WHEN 'VIEWER' THEN pa_role := 'guest';
                            ELSE pa_role := 'guest';
                        END CASE;

                        IF TG_OP = 'INSERT' THEN
                            SELECT id INTO pa_id FROM pyarchinit_users WHERE username = NEW.username;
                            IF pa_id IS NULL THEN
                                INSERT INTO pyarchinit_users (username, email, full_name, password_hash, role, is_active, created_at)
                                VALUES (NEW.username, NEW.email, NEW.full_name,
                                        COALESCE(NEW.hashed_password, '!needs_reset'),
                                        pa_role, COALESCE(NEW.is_active, true), NOW());
                            END IF;
                            RETURN NEW;

                        ELSIF TG_OP = 'UPDATE' THEN
                            UPDATE pyarchinit_users SET
                                full_name = NEW.full_name,
                                email = NEW.email,
                                role = pa_role,
                                is_active = COALESCE(NEW.is_active, true)
                            WHERE username = NEW.username;
                            IF NEW.hashed_password IS DISTINCT FROM OLD.hashed_password THEN
                                UPDATE pyarchinit_users SET password_hash = NEW.hashed_password WHERE username = NEW.username;
                            END IF;
                            RETURN NEW;

                        ELSIF TG_OP = 'DELETE' THEN
                            UPDATE pyarchinit_users SET is_active = false WHERE username = OLD.username;
                            RETURN OLD;
                        END IF;
                    END;
                    $$ LANGUAGE plpgsql
                """))

                session.execute(text("""
                    CREATE TRIGGER trg_sync_mini_to_pyarchinit_users
                        AFTER INSERT OR UPDATE OR DELETE ON users
                        FOR EACH ROW EXECUTE FUNCTION sync_mini_to_pyarchinit_users()
                """))

                # --- Initial sync: copy pyarchinit_users → users (missing ones) ---
                session.execute(text("""
                    INSERT INTO users (username, email, full_name, hashed_password, role, is_active, created_at)
                    SELECT pu.username, pu.email, pu.full_name,
                           COALESCE(pu.password_hash, '!needs_reset'),
                           CASE LOWER(pu.role)
                               WHEN 'admin' THEN 'ADMIN'
                               WHEN 'responsabile' THEN 'ADMIN'
                               WHEN 'archeologo' THEN 'OPERATOR'
                               WHEN 'studente' THEN 'OPERATOR'
                               WHEN 'guest' THEN 'VIEWER'
                               ELSE 'VIEWER'
                           END,
                           COALESCE(pu.is_active, true), NOW()
                    FROM pyarchinit_users pu
                    WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.username = pu.username)
                """))

                # --- Initial sync: copy users → pyarchinit_users (missing ones) ---
                session.execute(text("""
                    INSERT INTO pyarchinit_users (username, email, full_name, password_hash, role, is_active, created_at)
                    SELECT u.username, u.email, u.full_name,
                           COALESCE(u.hashed_password, '!needs_reset'),
                           CASE UPPER(u.role)
                               WHEN 'ADMIN' THEN 'admin'
                               WHEN 'OPERATOR' THEN 'responsabile'
                               WHEN 'VIEWER' THEN 'guest'
                               ELSE 'guest'
                           END,
                           COALESCE(u.is_active, true), NOW()
                    FROM users u
                    WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_users pu WHERE pu.username = u.username)
                """))

                session.commit()
                logger.info("User sync triggers created + initial sync completed")
                return 1

        except Exception as e:
            logger.warning(f"migrate_user_sync_trigger: {e}")
            return 0

    def migrate_all_tables(self):
        """Run all necessary migrations"""
        try:
            logger.info("Starting database migrations...")

            total_migrations = 0

            # Migrate inventario_materiali_table
            total_migrations += self.migrate_inventario_materiali_table()

            # Add i18n columns
            total_migrations += self.migrate_i18n_columns()

            # Add tipo_documento and file_path columns to US table
            total_migrations += self.migrate_tipo_documento()

            # Add other table migrations here as needed

            # Add concurrency columns to all tables
            total_migrations += self.migrate_concurrency_columns()

            # Add missing inventario columns
            total_migrations += self.migrate_inventario_extra_columns()

            # Add missing US columns
            total_migrations += self.migrate_us_extra_columns()

            # Convert us_table.us from VARCHAR(100) to TEXT
            total_migrations += self.migrate_us_column_to_text()

            # Add contact fields to users table (BEFORE trigger so schema is ready)
            try:
                for col, typ in [('telegram_username', 'VARCHAR(100)'), ('phone', 'VARCHAR(30)')]:
                    if not self.check_column_exists('users', col):
                        with self.connection.get_session() as session:
                            session.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typ}"))
                            session.commit()
                            logger.info(f"Added column {col} to users table")
                            total_migrations += 1
            except Exception as e:
                logger.warning(f"Could not add contact columns to users: {e}")

            # Bidirectional user sync trigger (PostgreSQL only)
            total_migrations += self.migrate_user_sync_trigger()

            logger.info(f"All migrations completed. Total migrations applied: {total_migrations}")
            return total_migrations

        except Exception as e:
            logger.error(f"Error during database migrations: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure"""
        try:
            inspector = inspect(self.connection.engine)
            
            # Check if table exists
            if not inspector.has_table(table_name):
                return {'exists': False}
            
            # Get columns info
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            return {
                'exists': True,
                'columns': columns,
                'column_names': column_names,
                'column_count': len(columns)
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {'exists': False, 'error': str(e)}
    
    def check_migration_needed(self, table_name: str, required_columns: List[str]) -> List[str]:
        """Check which columns are missing from a table"""
        try:
            table_info = self.get_table_info(table_name)
            
            if not table_info['exists']:
                return required_columns  # All columns are missing if table doesn't exist
            
            existing_columns = table_info['column_names']
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            return missing_columns
            
        except Exception as e:
            logger.error(f"Error checking migration for {table_name}: {e}")
            return required_columns