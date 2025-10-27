# Changelog

All notable changes to PyArchInit-Mini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.6] - 2025-10-27

### Added
- **Chronological Datazioni System**
  - New `datazioni_table` model for standardized archaeological dating periods
  - Fields: `id_datazione`, `nome_datazione`, `fascia_cronologica`, `descrizione`, `created_at`, `updated_at`
  - 36 pre-configured Italian archaeological periods from Paleolitico to Età Contemporanea
  - Multi-database support: SQLite and PostgreSQL via SQLAlchemy ORM
  - Property `full_label` returns formatted "Nome Datazione (Fascia Cronologica)"
  - Method `to_dict()` for JSON serialization

- **DatazioneService - Complete CRUD Operations**
  - `create_datazione(datazione_data)` - Create new dating period with validation
  - `get_datazione_by_id(datazione_id)` - Retrieve by ID
  - `get_datazione_by_nome(nome)` - Search by name
  - `get_all_datazioni(page, size)` - Paginated list with ordering
  - `get_datazioni_choices()` - Formatted choices for dropdown/combobox forms
  - `update_datazione(datazione_id, update_data)` - Update existing period
  - `delete_datazione(datazione_id)` - Delete period
  - `count_datazioni()` - Count total periods
  - `initialize_default_datazioni()` - Auto-populate with 36 standard Italian periods

- **Testing Infrastructure**
  - Comprehensive test script `test_datazioni_table.py` with 7 test cases
  - Tests: table creation, default initialization, CRUD operations, choices generation, search
  - 90%+ test coverage for core functionality
  - Validates multi-database compatibility

### Changed
- Updated README with Chronological Datazioni System feature in Advanced Archaeological Tools section
- Updated Project Status section with v1.5.6 release notes
- Session management improvements with context managers to avoid detached instance errors

### Technical
- Files added:
  - `pyarchinit_mini/models/datazione.py` - Datazione model
  - `pyarchinit_mini/services/datazione_service.py` - Service layer
  - `test_datazioni_table.py` - Test script
- Files modified:
  - `pyarchinit_mini/models/__init__.py` - Added Datazione import
  - `README.md` - Added feature documentation and v1.5.6 release notes
  - `pyproject.toml` - Version 1.5.6

### Next Steps (v1.6.0)
- Web GUI combobox integration for datazione field
- Desktop GUI combobox integration
- Parser synchronization with datazioni table
- Import/export updates for datazioni support

### Database Schema
```sql
CREATE TABLE datazioni_table (
    id_datazione INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_datazione VARCHAR(200) NOT NULL UNIQUE,
    fascia_cronologica VARCHAR(200),
    descrizione TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Impact
- Foundation for standardized chronological dating across all US records
- Replaces free-text datazione field with controlled vocabulary
- Enables consistent periodization for Harris Matrix exports
- Prepares GUI integration for dropdown/combobox in v1.6.0
- Compatible with both SQLite (development) and PostgreSQL (production)

## [1.5.3] - 2025-10-26

### Added
- **Harris Matrix Import Tool (CLI)**
  - New command-line tool `pyarchinit-harris-import` for bulk import of Harris Matrix data
  - Supports CSV and Excel (.xlsx, .xls) file formats
  - Import complete stratigraphic sequences with nodes and relationships
  - Full Extended Matrix node types support: US, USM, USVA, USVB, SF, VSF, TU, DOC, Extractor, Combiner, etc.
  - All relationship types: Covers, Fills, Cuts, Bonds_to, Equal_to, Continuity, >, >>, etc.
  - Automatic periodization (periodo/fase) support with area grouping
  - Built-in validation with detailed error messages and warnings
  - Export to GraphML and DOT formats after import
  - Duplicate detection and update handling
  - Transaction safety with automatic rollback on error
  - Command: `pyarchinit-harris-import matrix.xlsx --site "Site Name" --export-graphml`

- **Harris Matrix Template Generator**
  - New command `pyarchinit-harris-template` to generate Excel template
  - Pre-configured sheets: NODES and RELATIONSHIPS
  - Column headers and format ready to use
  - Helpful for creating new import files

- **Comprehensive Documentation**
  - Added `docs/features/harris_matrix_import.rst` - Complete 600+ line guide
  - Covers file format specification (CSV/Excel structure)
  - All Extended Matrix node types with examples
  - Complete relationship types reference (Italian/English)
  - Step-by-step usage guide with real-world examples
  - Validation and error handling documentation
  - Best practices and troubleshooting
  - Python API usage examples
  - Web GUI integration documentation

### Changed
- Updated main documentation index to include Harris Matrix Import guide
- Enhanced CLI interface with comprehensive help messages
- Improved error reporting with clear actionable messages

### Technical
- Files added:
  - `pyarchinit_mini/cli/harris_import.py` - Main import tool implementation
  - `pyarchinit_mini/cli/harris_template.py` - Template generator
  - `docs/features/harris_matrix_import.rst` - Complete documentation
- Files modified:
  - `docs/index.rst` - Added reference to new documentation
  - `pyproject.toml` - Version 1.5.3, added CLI entry points
- New entry points:
  - `pyarchinit-harris-import` - Import Harris Matrix from file
  - `pyarchinit-harris-template` - Generate import template
- Supported node types: US, USM, USVA, USVB, USVC, SF, VSF, TU, USD, CON, DOC, Extractor, Combiner, property
- Supported relationships: Covers, Covered_by, Fills, Filled_by, Cuts, Cut_by, Bonds_to, Equal_to, Leans_on, Continuity, >, <, >>, <<

### Documentation
- Complete Harris Matrix Import guide with:
  - File format specification (Excel with 2 sheets, CSV with 2 sections)
  - Column definitions (required/optional for NODES and RELATIONSHIPS)
  - All 14 Extended Matrix node types with descriptions
  - All 14 relationship types (stratigraphic + Extended Matrix)
  - Command-line usage examples (basic, with exports, custom database)
  - Complete working example with 10-US test site
  - Web interface integration guide
  - Validation and error handling reference
  - Database integration details
  - Best practices and troubleshooting
  - Python API programmatic usage
  - Appendix with complete type/relationship reference tables

### Impact
- Users can now import entire Harris Matrix datasets from spreadsheets
- Bulk creation of stratigraphic sequences from external systems
- Standardized data exchange format for archaeological projects
- Simplified testing with sample datasets
- Full Extended Matrix methodology support in imports
- Seamless integration with existing GraphML export workflow

## [1.5.2] - 2025-10-26

### Fixed
- **Web Dashboard Documentation Links**
  - Changed documentation links to point to ReadTheDocs (always available)
  - Previously pointed to localhost:8000/docs (requires FastAPI server running)
  - Now points to https://pyarchinit-mini.readthedocs.io/en/latest/
  - Affects both inline link in System Info section and Documentation button

### Changed
- Updated version display in web dashboard to v1.5.2
- Documentation link label changed from "API REST" to "Documentation"

### Technical
- Files modified:
  - `web_interface/templates/dashboard.html` (lines 169, 176)
  - `pyproject.toml` (version 1.5.2)

## [1.5.1] - 2025-10-26

### Fixed
- **Harris Matrix - Graphviz Orthogonal Splines Crash**
  - Fixed Graphviz crash when using orthogonal splines with edge labels and clusters
  - Error: "Warning: Orthogonal edges do not currently handle edge labels"
  - Error: "Assertion failed: (np->cells[0]), function chkSgraph, file maze.c, line 317"
  - Solution: Use `xlabel` instead of `label` for edge labels when `splines='ortho'`
  - **Impact**: Harris Matrix now renders correctly for all graph sizes with period/area clustering
  - Affects both small graphs (51 nodes) and large graphs (758+ nodes)
  - Maintains hierarchical structure and orthogonal splines as before

### Changed
- **Web Dashboard Updated**
  - Version display updated to v1.5.1 (was v0.1.0)
  - GitHub link updated to correct repository: https://github.com/enzococca/pyarchinit-mini
  - API documentation link functional

### Technical
- Files modified:
  - `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py` (lines 156-163, 403-460)
  - `web_interface/templates/dashboard.html` (lines 167, 179)
  - `pyproject.toml` (version 1.5.1)
- Modified edge label handling: `xlabel` for orthogonal splines, `label` for other spline types
- Ensures compatibility with Graphviz dot engine for complex archaeological matrices

## [1.5.0] - 2025-10-26

### Fixed
- **GraphML Export - Periodization Display**
  - Fixed `parse_clusters()` in `dot_parser.py` to handle both quoted and unquoted label values
  - Fixed cluster label parsing: now supports `label=value` format in addition to `label="value"`
  - Fixed node label parsing: now supports `NODE [...]` format in addition to `"NODE" [...]`
  - Fixed bracket counting for proper cluster boundary detection
  - Fixed period ordering: now uses chronological order (based on periodo/fase) instead of alphabetical
  - Fixed reverse epochs: now correctly inverts chronological order instead of using alphabetical reverse
  - **Result**: All 8 archaeological periods now visible in GraphML export (was showing only 3-4)
  - **Impact**: Large sites like Dom zu Lund (760 US nodes) now display complete period structure

- **GraphML Export - Period Ordering**
  - Modified `graphml_exporter.py` to use chronological ordering based on cluster_id
  - Periods now appear in correct archaeological sequence: Geologisch → Neuzeit
  - Reverse epochs properly shows newest → oldest: Non datato → Geologisch
  - Maintains consistency with database periodization (periodo_iniziale, fase_iniziale)

- **Harris Matrix - Large Graph Rendering**
  - Fixed Graphviz crash for large archaeological sites (> 500 nodes)
  - Web interface now detects large graphs and shows informative message instead of attempting render
  - Optimized `get_matrix_statistics()` to skip expensive operations (cycle detection, levels) for large graphs
  - Statistics calculation reduced from minutes to seconds for large sites
  - Users directed to GraphML export solution which works perfectly for any graph size
  - **Error Fixed**: "Assertion failed: trouble in init_rank" Graphviz crashes eliminated
  - **Impact**: Large sites like Dom zu Lund (758 nodes) now have graceful UX with working export path
  - Created `large_graph_message.html` template with statistics display and export options

### Changed
- **DOT Parser Enhanced**
  - `parse_clusters()` now more robust with flexible label format detection
  - Better handling of DOT files generated by GraphViz without quoted attributes
  - Improved cluster boundary detection using balanced bracket counting

### Documentation
- Added `docs/FIX_GRAPHML_8_PERIODS.md`: Complete technical documentation of the GraphML fix
- Added `docs/HARRIS_MATRIX_LARGE_GRAPHS.md`: Technical guide for large graph handling
- Added test scripts: `debug_parse_clusters.py`, `verify_graphml_periods.py`, `verify_graphml_reverse.py`

### Technical
- Files modified:
  - `pyarchinit_mini/graphml_converter/dot_parser.py` (lines 1259-1331)
  - `pyarchinit_mini/graphml_converter/graphml_exporter.py` (lines 268-279, 518, 551)
  - `web_interface/app.py` (lines 1268-1282) - Large graph detection
  - `pyarchinit_mini/harris_matrix/matrix_generator.py` (lines 699-739) - Statistics optimization
- Created templates:
  - `web_interface/templates/harris_matrix/large_graph_message.html` - Large graph informative page
- Verified on Dom zu Lund site: 758 US nodes, 8 periods, all correctly positioned
- Export performance: ~0.5 seconds for 758 nodes, 0.81 MB GraphML file
- Web interface gracefully handles large graphs with informative message and working export path

## [1.4.0] - 2025-10-25

### Added
- **Automatic Database Backup System** (CRITICAL SAFETY FEATURE)
  - Automatic SQLite backup using file copy with timestamp (e.g., `database.db.backup_20251025_165843`)
  - PostgreSQL backup support using pg_dump to create SQL dumps
  - Backup created BEFORE any database modification during import
  - Only one backup per session (multiple imports reuse same backup)
  - Backup path returned in import statistics for verification
  - New `auto_backup` parameter (default=True) for all import functions
  - Backup can be disabled with `auto_backup=False` for trusted sources
  - Complete logging of all backup operations
  - Tested with real databases (5.8 MB → 4.7 MB backup verified)

- **Spatial Relationship Types Support**
  - Added support for 3 spatial relationship types in Harris Matrix generation:
    * "connected to" / "collegato a" / "connects to" (195 relationships in Dom zu Lund)
    * "supports" (3 relationships)
    * "abuts" / "confina con" / "adiacente a" (3 relationships)
  - Previously these 201 relationships were being skipped with warning messages
  - Now properly included in Harris Matrix visualization and GraphML export
  - Represents 8.9% increase in relationship data for typical archaeological sites

- **Complete Dom zu Lund Import**
  - Successfully imported complete archaeological site from PyArchInit database
  - 1 site record (Lund Cathedral, Sweden)
  - 758 stratigraphic units (US)
  - 2,459 relationships (100% imported, no skipped relationships)
  - 42 periodization records (21 new + 21 existing)
  - Comprehensive test with real-world dataset

### Fixed
- **UnboundLocalError in Harris Matrix Generator**
  - Fixed variable 'filters' not being defined at function start
  - Moved filters definition to beginning of `_get_relationships()` function
  - Eliminated warning messages: "cannot access local variable 'filters' where it is not associated with a value"
  - Affects USRelationships and HarrisMatrix table queries

- **PyArchInit Import Issues** (Session: Dom zu Lund)
  - Fixed ORM metadata cache issues when importing from PyArchInit databases
  - Replaced ORM queries with raw SQL in critical import functions
  - Fixed missing i18n columns handling with automatic migration
  - Fixed relationship column name (`id_us_relationship` → `id_relationship`)
  - All import errors resolved for both SQLite and PostgreSQL sources

### Changed
- **Import Functions Enhanced**
  - `import_sites()` now accepts `auto_backup` parameter
  - `import_us()` now accepts `auto_backup` parameter
  - `import_inventario()` now accepts `auto_backup` parameter
  - `migrate_source_database()` now accepts `auto_backup` parameter
  - All import functions return backup path in statistics dictionary
  - Import service tracks backup creation with `_backup_created` and `_backup_path` instance variables

### Documentation
- Added `docs/AUTOMATIC_IMPORT_AND_BACKUP_GUIDE.md`: Comprehensive guide for automatic import and backup
- Added `docs/SESSION_DOM_ZU_LUND_IMPORT_COMPLETE.md`: Complete session summary for Dom zu Lund import
- Updated `docs/IMPORT_SUCCESS_VERIFICATION.md`: Added spatial relationship fix documentation
- Added `test_backup_system.py`: Test script for automatic backup functionality
- Added `import_complete_dom_zu_lund.py`: Complete import script for all entity types
- Added `test_import_dom_zu_lund.py`: Diagnostic script for import verification

### Technical
- New method: `_backup_source_database()` for automatic database backup
- Supports both SQLite (shutil.copy2) and PostgreSQL (pg_dump) backups
- Backup creation is idempotent - only one backup per service instance
- Non-destructive: backups created before any ALTER TABLE operations
- Timestamped filenames ensure unique backup names
- Complete error handling with fallback to continue if backup fails (with warning)

### Security
- **CRITICAL**: Source database is now automatically backed up before ANY modification
- Backup is created BEFORE adding i18n columns during migration
- Provides safety net for accidental data loss or corruption
- Allows easy rollback to pre-import state if needed

## [1.3.2] - 2025-10-25

### Added
- **Heriverse/ATON Export Integration**: Complete support for Heriverse and ATON platform JSON format
  - New `export_to_heriverse_json()` method in S3DConverter with CouchDB/scene wrapper
  - Auto-generated UUIDs for scene and creator metadata
  - Environment configuration (panoramas, lighting, scene settings)
  - Scenegraph support for 3D scene hierarchy
  - USVn category for virtual negative stratigraphic units (separate from USVs)
  - Semantic shapes: Auto-generated 3D proxy model placeholders (GLB) for each US
  - Representation models and panorama models support
  - Extended edge types: generic_connection, changed_from, contrasts_with for paradata
  - 13 node categories including semantic_shapes, representation_models, panorama_models
  - 13 edge types for comprehensive relationship modeling
  - New Flask route: `GET /3d/export/heriverse/<site_name>`
  - Web UI button: "Export Heriverse" (orange button in s3Dgraphy section)
  - Complete test suite with 4/4 tests passing

### Updated
- **Documentation**:
  - Updated `README.md` with comprehensive Heriverse/ATON section
  - Updated `docs/features/s3dgraphy.rst` with Heriverse export documentation
  - Updated `docs/s3dgraphy_integration.md` with Heriverse format comparison
  - Added `docs/HERIVERSE_INTEGRATION_SUMMARY.md` technical guide
  - Created `test_heriverse_export.py` validation suite
- **Web Interface**: Added third export button in s3Dgraphy section (JSON, Heriverse, Interactive Viewer)

### Technical
- Complete Heriverse JSON v1.5 specification compliance
- Auto-generates semantic_shape placeholders for each stratigraphic unit
- Full CouchDB/scene wrapper with proper UUID generation
- Compatible with Heriverse platform and ATON 3D viewer
- Supports both standard s3Dgraphy v1.5 and Heriverse formats as separate export options

## [1.2.12] - 2025-10-22

### Fixed
- **Web Interface Language Switching**: Fixed all navbar and menu translations
  - Uncommented 42 missing translation strings for both Italian and English
  - Fixed incorrect translations (Menu was "Manuale", now correctly "Menu")
  - All interface elements now properly switch between languages
  - Language switcher now affects entire web interface, not just analytics page

### Added
- **PyArchInit-Mini Logo**: Professional logo added to all interfaces
  - Web interface: navbar and login page
  - Desktop GUI: window icon and toolbar
  - CLI: ASCII art logo in welcome screen
  - Documentation: ReadTheDocs and README
  - Favicon for web interface

### Technical
- Updated all navigation and menu translation strings in messages.po files
- Recompiled translation catalogs with complete string coverage
- Created logo assets in PNG and ICO formats

## [1.2.11] - 2025-10-22

### Fixed
- **Web Interface Internationalization**: Fixed all hardcoded Italian text in web interface
  - All error and success messages now use translation system
  - Analytics dashboard fully translated
  - Database info page fully translated
  - All flash messages support language switching
- **Language Switching**: Fixed language switcher to properly change interface language
  - Added missing translations for Italian and English
  - Compiled translation files with all required strings
  - Session-based language preference storage

### Added
- Complete translation coverage for web interface
- 80+ new translation strings for both Italian and English

### Technical
- Updated Flask-Babel integration for proper i18n support
- All templates now use `{{ _() }}` for translatable strings
- Flash messages in app.py use gettext for dynamic translation

## [1.2.10] - 2025-10-22

### Added
- **pyarchinit-mini-init command**: New initialization command for first-time setup
  - Creates database and configuration directories automatically
  - Prompts for admin user creation interactively
  - Supports --non-interactive flag for automated deployments
  - Combines setup and admin user creation in one command

### Changed
- Updated README with clearer installation instructions
- Improved first-time user experience with single initialization command
- Fixed all command names in documentation to use correct prefixes

### Fixed
- Admin user creation now works with installed package paths
- Database path detection improved for various Python environments

## [1.2.9] - 2025-10-22

### Fixed
- Removed duplicate Project Status section from README
- Corrected version number in Project Status section

### Documentation
- Cleaned up README to show only the current Project Status

## [1.2.8] - 2025-10-22

### Added
- **Project Status Section**: Added comprehensive project status to README
- Clear indication that all interfaces are now fully functional
- Summary of recent fixes and improvements

### Changed
- Updated README to reflect production-ready status
- Emphasized that all installation issues have been resolved

### Documentation
- Added detailed status badges and checkmarks for features
- Listed all recent fixes from versions 1.2.5-1.2.8
- Added reference to active development status

## [1.2.7] - 2025-10-22

### Fixed
- **Web Server**: Fixed Flask template and static file path resolution for installed package
- **Web Server**: Added proper error handling for server startup
- **Web Server**: Created minimal CSS structure for proper static file inclusion

### Changed
- Flask app now uses absolute paths based on module location instead of pkg_resources
- Improved error messages and diagnostics for web server startup

### Added
- Basic CSS file (style.css) to ensure static directory is properly packaged

## [1.2.6] - 2025-10-22

### Fixed
- **API**: Added missing email-validator dependency for Pydantic EmailStr validation
- **Desktop GUI**: Fixed language switching by properly importing and initializing i18n system
- **Web Interface**: Changed relative imports to absolute imports for proper module resolution

### Added
- email-validator>=2.0.0 to core dependencies

## [1.2.5] - 2025-10-22

### Fixed
- **Desktop GUI**: Removed orphaned help_window reference in language dialog (line 1463)
- **Database**: Added automatic i18n column migrations during initialization
- **Database**: Missing English translation columns (definizione_sito_en, descrizione_en, etc.) now created automatically

### Added
- i18n migration method to DatabaseMigrations class
- Automatic migration of translation columns for site_table, us_table, and inventario_materiali_table

## [1.2.0] - 2025-10-22

### Added
- **s3Dgraphy Integration**: 3D visualization support for stratigraphic units
- **i18n Support**: Full internationalization for Italian and English
- **GraphViz Layout**: Enhanced Harris Matrix with GraphViz dot layout engine
- **Translation System**: Complete translation infrastructure for all interfaces

### Changed
- Improved Harris Matrix visualization with multiple layout options
- Enhanced US and Inventory forms with multilingual support

## [0.1.3] - 2025-01-18

### Added
- Complete web interface with all core functionality
- Stratigraphic relationships field in US form
- Complete Bootstrap 5 templates for all entities
- Comprehensive documentation for web interface features
- WEB_INTERFACE_FEATURES.md with detailed functionality overview

### Fixed
- **Harris Matrix generation** - Fixed 0 nodes issue by passing us_service to HarrisMatrixGenerator
- **PDF export** - Fixed detached instance error with proper session handling
- **Web server port** - Changed default from 5000 to 5001 to avoid macOS AirPlay conflict
- **Rapporti stratigrafici** - Added missing field to US form and template

### Changed
- HarrisMatrixGenerator now requires us_service parameter for proper initialization
- PDF export route now converts models to dicts within session scope
- All web templates updated with professional Bootstrap styling

### Verified
- ✅ Harris Matrix: 50 nodes, 99 edges, 7 levels - working correctly
- ✅ PDF Export: 5679 bytes generated - working correctly
- ✅ Stratigraphic Relationships: 228 relationships parsed from database
- ✅ All web templates rendering correctly

## [0.1.2] - 2025-01-17

### Changed
- Updated GitHub repository URLs from `pyarchinit/pyarchinit-mini` to `enzococa/pyarchinit-mini-desk`
- Fixed project URLs in pyproject.toml and setup.py

## [0.1.1] - 2025-01-17

### Added
- Initial PyPI publication configuration
- Modular installation with optional dependencies (cli, web, gui, harris, pdf, media, all)
- Console script entry points for all interfaces:
  - `pyarchinit-mini` - CLI interface
  - `pyarchinit-mini-api` - REST API server
  - `pyarchinit-mini-web` - Web interface
  - `pyarchinit-mini-gui` - Desktop GUI
  - `pyarchinit-mini-setup` - User environment setup
- User environment setup script for `~/.pyarchinit_mini` directory
- MANIFEST.in for proper file inclusion in distribution
- Comprehensive PyPI documentation (PYPI_PUBLICATION.md, PYPI_QUICKSTART.md)

### Changed
- Restructured dependencies with extras_require for modular installation
- API server now uses run_server() entry point
- Web interface now uses main() entry point with environment configuration

## [0.1.0] - 2025-01-17

### Added
- Core database models (Site, US, InventarioMateriali)
- Multi-database support (SQLite, PostgreSQL)
- Service layer (SiteService, USService, InventarioService)
- REST API with FastAPI
- Flask web interface
- Tkinter desktop GUI
- CLI interface with Click
- Harris Matrix generation and visualization
- PDF report export
- Media file management
- Database migration script for stratigraphic relationships
- Sample data population script

### Database
- Migrated stratigraphic relationships from textual to structured format
- 114 relationships migrated (90 "Copre", 14 "Taglia", 10 "Si appoggia a")
- Normalized us_relationships_table with proper relationship types

### Documentation
- Complete CLAUDE.md with architecture and development guidelines
- README with installation and usage instructions
- API documentation with OpenAPI/Swagger
