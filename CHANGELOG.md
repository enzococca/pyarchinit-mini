# Changelog

All notable changes to PyArchInit-Mini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.11] - 2025-11-02

### Added - CRUD + Validation Tools
- **Complete Data Management System**
  - Unified `manage_data` MCP tool with 6 operations
  - `get_schema`: Database schema inspector with constraints and sample values
  - `insert`: Create new archaeological records with full validation
  - `update`: Modify existing records by ID or filters
  - `delete`: Safe deletion with dry-run and cascade warnings
  - `upsert`: Intelligent conflict resolution (insert or update)
  - `validate_stratigraphy`: Stratigraphic relationship validator with auto-fix

- **Database Operations**
  - Field validation (required fields, data types, constraints)
  - Foreign key validation and referential integrity checks
  - Auto-increment field detection (SQLite and PostgreSQL)
  - Transaction safety with automatic rollback on errors
  - Partial updates (only modify specified fields)
  - Dry-run modes for all destructive operations

- **Stratigraphic Validation**
  - Paradox detection (contradictory relationships)
  - Cycle detection in Harris Matrix (temporal paradoxes)
  - Missing reciprocal relationship detection
  - Chronological consistency validation with periodization data
  - Auto-fix for missing reciprocals
  - Error categorization (paradoxes, cycles, chronology, other)
  - Re-validation after auto-fixes with improvement metrics
  - Support for Italian and English relationship types

- **Conflict Resolution (UPSERT)**
  - Detect duplicates by composite keys
  - 4 resolution strategies: detect, skip, update, upsert
  - 3 merge strategies: prefer_new, prefer_existing, replace_all
  - Atomic operations (no race conditions)
  - Intelligent data merging

- **Documentation**
  - `CRUD_TOOLS.md`: Comprehensive guide (500+ lines)
  - Complete API reference for all 6 operations
  - Best practices and error handling
  - Usage examples and common patterns
  - Architecture documentation
  - `MCP_TOOLS_REFERENCE.md`: Complete MCP tools reference (1465 lines, 41KB)
  - Documentation for all 14 MCP tools
  - Parameter specifications and return values
  - Usage examples for each tool
  - Best practices and troubleshooting
  - Tool categorization and quick reference table
  - Updated `docs/MCP_INTEGRATION.md` with links to tool reference

- **Testing**
  - `test_crud_tools.py`: Full test suite (330 lines)
  - 11 test operations covering all functionality
  - All tests passing (59 US validated, 0 errors)
  - Dry-run and actual execution tests
  - Foreign key and constraint validation tests

### Fixed
- **Database Connection**
  - Fixed DatabaseManager initialization in all CRUD tools
  - Proper DatabaseConnection object creation
  - Correct engine reference pattern

### Changed
- **MCP Server**
  - Updated from 13 to 14 MCP tools
  - Added `manage_data` to tool registry
  - Updated server documentation

## [1.9.10] - 2025-11-02

### Added - AI Integration & 3D Visualization
- **Model Context Protocol (MCP) Integration**
  - Complete MCP server implementation for AI assistants (Claude Desktop, ChatGPT)
  - 5 MCP tools: `build_3d`, `filter`, `export`, `position`, `material`
  - 5 MCP resources: GraphML, US data, periods, relationships, sites
  - 3 MCP prompts: Stratigraphic Model, Period Visualization, US Description
  - HTTP/SSE transport for ChatGPT integration
  - stdio transport for Claude Desktop integration
  - Zero-config setup with `uvx` package runner
  - Natural language interface to archaeological data

- **3D Viewer (Browser-Based)**
  - Interactive Three.js r150 WebGL viewer in browser
  - Real-time 3D visualization of stratigraphic units
  - Chat interface for natural language commands (Italian/English)
  - Auto-populate US from site selection
  - GraphML-based positioning with Harris Matrix relationships
  - Color-coding by period, type, or custom colors
  - OrbitControls for camera navigation (rotate, zoom, pan)
  - View presets: Top, Front, Side, Isometric
  - Object selection with metadata display
  - Support for 3 positioning modes: GraphML, Simple, Grid
  - Adjustable layer spacing for vertical positioning

- **Blender Integration**
  - Real-time streaming addon for Blender 3.0+ (Socket.IO WebSocket)
  - Automatic 3D geometry generation based on US type
  - Professional material application (earth, stone, brick textures)
  - Color assignment by archaeological period
  - Different geometry for each US type: layers, walls, cuts, fills
  - Real-time sync between Blender and web viewer
  - Export to multiple formats: .blend, .glb, .fbx, .obj
  - AI-powered reconstruction with specialized agents
  - 4 AI agents: Architect, Validator, Texturizer, Reconstructor
  - Prompt generator for Claude AI site reconstruction

- **Comprehensive Documentation**
  - `docs/MCP_INTEGRATION.md` - Complete MCP setup guide (644 lines)
  - `docs/3D_VIEWER_GUIDE.md` - Browser 3D viewer guide (646 lines)
  - `docs/BLENDER_INTEGRATION.md` - Blender addon guide (645 lines)
  - Step-by-step setup instructions for all platforms
  - Multiple usage examples with screenshots
  - Troubleshooting sections for common issues
  - Complete API reference for developers

### Changed
- **MCP Configuration**: Switched from direct Python path to `uvx` package runner
  - Simplified Claude Desktop setup (no need to find Python path)
  - Auto-install PyArchInit-Mini on first run
  - Cross-platform compatibility (macOS, Linux, Windows)
  - Added `uvx` installation instructions for all platforms

- **Documentation Structure**
  - Updated `docs/index.rst` with new AI Integration & 3D Visualization section
  - Added quick links to MCP, 3D Viewer, and Blender guides
  - Integrated new documentation into ReadTheDocs
  - Updated README.md with AI Integration and 3D Visualization sections

- **Web Interface Enhancements**
  - New `/3d-builder/` route for browser-based 3D viewer
  - Socket.IO integration for real-time Blender streaming
  - Auto-populate US endpoint: `GET /api/sites/<site_name>/us`
  - Chat command parser for natural language queries
  - MCP executor for tool invocation from web interface

### Technical Details

**Backend:**
- New MCP server: `pyarchinit_mini/mcp_server/`
  - `server.py` - stdio MCP server (Claude Desktop)
  - `http_server.py` - HTTP/SSE MCP server (ChatGPT)
  - `tools/` - 5 MCP tool implementations
  - `proxy_generator.py` - 3D proxy object generation
  - `graphml_parser.py` - GraphML positioning parser
- New services:
  - `command_parser.py` - Natural language command parsing
  - `mcp_executor.py` - MCP tool execution from web interface

**Frontend:**
- New templates:
  - `templates/3d_builder/index.html` - 3D viewer interface
  - `templates/blender_viewer.html` - Blender real-time viewer
- New JavaScript:
  - `static/js/three-d-viewer.js` - Three.js viewer logic
  - `static/js/three.min.js` - Three.js r150 library
  - `static/js/OrbitControls.js` - Camera controls
- Socket.IO client integration for WebSocket communication

**Blender Addon:**
- `blender_addons/pyarchinit_realtime_streamer.py` - Real-time streaming addon
  - TCP socket listener (port 9876)
  - WebSocket client (Socket.IO)
  - Geometry generation based on US data
  - Material and color management
  - Real-time sync with web viewer

**Entry Points:**
- `pyarchinit-mini-mcp` - MCP server entry point (for uvx)
- MCP server accessible via uvx without installation

### Files Modified
- `docs/index.rst` - Added new documentation sections
- `docs/conf.py` - Verified Markdown support
- `README.md` - Updated with new features and roadmap
- `pyarchinit_mini/web_interface/app.py` - 3D builder routes, Socket.IO
- `pyarchinit_mini/web_interface/socketio_events.py` - WebSocket handlers
- `pyarchinit_mini/web_interface/three_d_builder_routes.py` - 3D viewer routes

### Files Added
- `docs/MCP_INTEGRATION.md` - MCP setup guide
- `docs/3D_VIEWER_GUIDE.md` - 3D viewer user guide
- `docs/BLENDER_INTEGRATION.md` - Blender integration guide
- `pyarchinit_mini/mcp_server/__main__.py` - MCP server entry point
- `pyarchinit_mini/services/command_parser.py` - Command parser
- `pyarchinit_mini/services/mcp_executor.py` - MCP executor
- `blender_addons/pyarchinit_realtime_streamer.py` - Blender addon
- `scripts/generate_3d_with_claude.py` - AI prompt generator

### Impact
- **AI Integration**: Natural language interface to archaeological data via Claude Desktop and ChatGPT
- **3D Visualization**: Interactive browser-based 3D viewer for stratigraphic units
- **Professional 3D Modeling**: Real-time Blender integration with AI-powered reconstruction
- **Zero-Config Setup**: uvx eliminates manual Python configuration
- **Cross-Platform**: Works on macOS, Linux, Windows with consistent experience
- **Real-Time Collaboration**: WebSocket streaming enables team collaboration
- **Enhanced Documentation**: 1,900+ lines of new user guides and technical documentation

### Upgrading from 1.8.6
- Update to version 1.9.10: `pip install --upgrade pyarchinit-mini`
- Install uvx: `brew install uv` (macOS) or see MCP_INTEGRATION.md
- Configure Claude Desktop with uvx (see docs/MCP_INTEGRATION.md)
- Install Blender addon (optional, see docs/BLENDER_INTEGRATION.md)

## [1.8.6] - 2025-10-31

### Added
- **Comprehensive Database Migration Conflict Resolution System**
  - **Automatic Backup System**: Creates timestamped backups before migration
    - SQLite: File copy with timestamp
    - PostgreSQL: Uses `pg_dump` for SQL backup
    - Configurable via `auto_backup` parameter (default: True)

  - **Conflict Detection**: Analyzes source and target databases for ID conflicts
    - Automatic primary key detection per table (handles id_sito, id_us, id_invmat, etc.)
    - Identifies conflicting IDs (exist in both databases)
    - Identifies new records (only in source)
    - Returns detailed statistics per table

  - **Three Merge Strategies**:
    - **Skip** (default): Skips records with conflicting IDs, preserves target data
    - **Overwrite**: Updates existing records with source data
    - **Renumber**: Generates new sequential IDs for conflicts, preserves all data

  - **New API Endpoints**:
    - `POST /api/pyarchinit/preview-migration-conflicts` - Preview conflicts before migration
    - Updated `/api/pyarchinit/migrate-database` - Now supports `merge_strategy` and `auto_backup` parameters

  - **Comprehensive Documentation**: Added `docs/DATABASE_MIGRATION_CONFLICTS.md`
    - API usage examples
    - Python code examples
    - Best practices and troubleshooting
    - Complete test coverage documentation

  - **Complete UI Integration**:
    - Visual merge strategy selector with 3 card-based options (Skip, Overwrite, Renumber)
    - "Preview Conflicts" button with detailed analysis modal
    - Auto-backup checkbox (enabled by default)
    - Bootstrap modal showing:
      - Conflict summary statistics
      - Intelligent recommendations based on conflict count
      - Table-by-table analysis with conflicting IDs
      - Responsive table design
    - Backup information display in success messages
    - Enhanced migration form with all new parameters

### Changed
- `ImportExportService.migrate_database()` signature updated with new parameters:
  - `merge_strategy`: `'skip'`, `'overwrite'`, or `'renumber'` (default: `'skip'`)
  - `auto_backup`: Boolean to enable/disable automatic backups (default: `True`)
- `ImportExportService._migrate_table()` completely rewritten to support conflict resolution strategies
- Migration response now includes backup information (path, size, status)

### Improved
- Database migration now provides detailed conflict analysis before proceeding
- Migration success rate improved with automatic conflict handling
- Data safety enhanced with automatic pre-migration backups
- Better error handling and logging for migration operations
- User experience significantly enhanced with visual feedback and preview capabilities
- JavaScript code quality improved with DRY principle (eliminated duplication)

### Technical Details
**Backend:**
- Added `_create_backup()` static method (lines 1820-1953 in import_export_service.py)
- Added `_detect_conflicts()` static method (lines 1955-2082 in import_export_service.py)
- Updated `_migrate_table()` with conflict resolution logic (lines 2197-2381)
- New test files with 100% pass rate:
  - `test_backup_system.py` (3/3 tests passing)
  - `test_conflict_detection.py` (comprehensive scenarios)
  - `test_conflict_detection_simple.py` (real database testing, 3/3 passing)
  - `test_merge_strategies.py` (3/3 tests passing)

**Frontend:**
- Updated `admin/database.html` template (+315 lines, -20 lines)
- Added JavaScript helper functions:
  - `buildMigrationRequestData()` - builds request with all parameters
  - `addSourceDatabaseFields()` - validates and adds source DB configuration
  - `addTargetDatabaseFields()` - validates and adds target DB configuration
- Added conflict preview modal with Bootstrap 5
- Integrated conflict preview API endpoint
- Enhanced migration form with new merge strategy and backup options
- All UI features tested with integration tests

## [1.8.5] - 2025-10-31

### Added
- **Default Database in Saved Connections**: Default SQLite database now automatically appears in "Saved Connections" section
  - Added initialization code in `app.py` to save active default database to ConnectionManager during startup
  - Default database persists across server restarts and is visible in Admin → Database Management
  - Resolves issue where only uploaded databases appeared in saved connections

### Improved
- **Complete English Translation for Database Management**: Fully translated the Database Management page to English
  - Translated all Italian strings in `admin/database.html` template
  - Added 30+ new translations to `messages.po` for both Italian and English
  - Sections now translated:
    - Database statistics (Sites, Stratigraphic Units, Inventory)
    - Database operations (Upload, Connect, Info)
    - Data migration section (SQLite ↔ PostgreSQL)
    - Saved connections table headers and actions
    - Help section
  - English interface now fully functional for database administration

### Changed
- Database Management UI now uses Flask-Babel translation functions throughout
- Compiled translation files (.mo) updated with new strings

## [1.8.4] - 2025-10-31

### Fixed
- **Windows bcrypt Compatibility**: Fixed bcrypt version incompatibility on Windows
  - Changed from `passlib[bcrypt]>=1.7.4` to `passlib>=1.7.4` + `bcrypt>=4.0.0,<4.1.0`
  - Resolves: `AttributeError: module 'bcrypt' has no attribute 'about'`
  - Resolves: `ValueError: password cannot be longer than 72 bytes`
  - Ensures bcrypt 4.0.x is installed (compatible with passlib 1.7.4)
  - Updated in both `web` and `all` dependency groups

### Technical Details
- passlib 1.7.4 is not compatible with bcrypt 4.1.0+
- On Windows, `passlib[bcrypt]` was installing bcrypt 4.1.x or 4.2.x
- Explicit version constraint ensures compatible bcrypt version
- Improves Windows installation reliability

## [1.8.3] - 2025-10-31

### Fixed
- **Web Interface Dependencies**: Added authentication dependencies to `web` optional dependency group
  - Added `passlib[bcrypt]>=1.7.4` to web dependencies
  - Added `python-jose[cryptography]>=3.3.0` to web dependencies
  - Added `flask-login>=0.6.3` to web dependencies
  - Resolves: `ImportError: passlib is required for password hashing` when installing with `pip install pyarchinit-mini[web]`
  - Web interface now works correctly on Windows without requiring separate `pip install pyarchinit-mini[web,auth]`

### Changed
- Web interface installation is now self-contained with all required dependencies
- Users can install with just `pip install pyarchinit-mini[web]` and have full authentication support

### Technical Details
- Authentication libraries were previously only in `auth` and `all` dependency groups
- Web interface requires authentication for login, so these dependencies are now included in `web` group
- Improves user experience by reducing installation steps

## [1.8.2] - 2025-10-31

### Fixed
- **Italian Translation**: Corrected "Media Files" translation in dashboard from "ha modificato US" to "File Multimediali"
  - Fixed in `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po` line 934
  - Compiled updated translation files (.mo)

- **Windows Installation**: Fixed passlib dependency error on Windows
  - Changed from separate `passlib>=1.7.4` + `bcrypt>=4.0.0,<4.1.0` to unified `passlib[bcrypt]>=1.7.4`
  - Updated in both `auth` and `all` dependency groups in `pyproject.toml`
  - Resolves: "Error creating admin user: passlib is required for password hashing. Install with: pip install 'passlib[bcrypt]'"
  - Ensures bcrypt backend is properly installed on all platforms, especially Windows

### Technical Details
- Translation files properly compiled with pybabel
- Dependencies now correctly specify bcrypt as a passlib extra
- Improves cross-platform compatibility (macOS, Linux, Windows)

## [1.8.1] - 2025-10-30

### Fixed - Database Migration Hotfix
- **Critical Bug**: Fixed missing `tipo_documento` and `file_path` columns in existing databases
  - Root cause: `DatabaseMigrations.migrate_all_tables()` was not calling the tipo_documento migration
  - Added `migrate_tipo_documento()` method to `pyarchinit_mini/database/migrations.py`
  - Updated `migrate_all_tables()` to include tipo_documento migration
  - Ensures compatibility with databases created before version 1.8.0
  - Users upgrading from versions prior to 1.8.0 will now have columns added automatically
  - Resolves `sqlite3.OperationalError: no such column: us_table.tipo_documento` error

### Technical Details
- Migration script `add_tipo_documento.py` existed but was not being executed
- Adds two columns to `us_table`:
  - `tipo_documento` VARCHAR(100) - Document type classification
  - `file_path` TEXT - Path to associated document files
- Migration uses safe `add_column_if_not_exists()` method to prevent duplicate column errors

## [1.8.0] - 2025-10-30

### Added - Enhanced Media Management System
- **Image Viewer**: GLightbox 3.2.0 integration with gallery support
  - Separate galleries per entity type (sites, US, inventario)
  - Lightbox navigation with touch support
  - Thumbnail generation and preview
- **PDF Viewer**: In-browser PDF viewing with GLightbox iframe support
- **Video Viewer**: Native HTML5 video playback with GLightbox
  - Support for 10 video formats: MP4, AVI, MOV, WMV, FLV, WebM, MKV, M4V, MPEG, MPG
  - Fullscreen playback and controls
- **Excel/CSV Viewer**: pandas-powered spreadsheet viewer
  - Bootstrap-styled HTML tables
  - Supports up to 1000 rows
  - Preserves formatting and data types
- **DOCX Viewer**: python-docx HTML converter
  - Table support with Bootstrap styling
  - Heading detection and conversion
  - Opens in new window for better screen space
- **3D Model Viewer**: Interactive Three.js r147 viewer
  - OrbitControls for navigation (rotate, pan, zoom)
  - Support for 6 formats: OBJ, STL, PLY, GLTF, GLB, DAE
  - Wireframe toggle and reset view features
  - Opens in new window for immersive experience
- **Media Deletion**: Delete functionality across all interfaces
  - Available in media list view
  - Available in all entity forms (sites, US, inventario)
  - JavaScript confirmation before deletion
  - Smart redirect logic (returns to form if deleted from edit page)
  - CSRF protection on all delete operations

### Changed
- **Video Detection**: Enhanced file type recognition by extension
  - Improved detection for 10 video formats in `MediaHandler._determine_media_type()`
  - More reliable than MIME-type based detection
- **Media Organization**: Automatic file organization by entity type and ID
  - Separate galleries prevent cross-entity media mixing
  - Consistent viewer interface across all entity forms
- **Dependencies**: Added media viewing libraries
  - `python-docx>=1.0.0` for DOCX viewing
  - `pandas>=2.0.0` for Excel/CSV parsing (already in export dependencies)
  - `openpyxl>=3.1.0` for Excel file support
  - GLightbox 3.2.0 loaded from CDN for image/PDF/video lightbox
  - Three.js r147 loaded from CDN for 3D model rendering

### Technical Details
- Complex viewers (DOCX, Excel, 3D) open in new window (`target="_blank"`)
- Simple viewers (images, PDF, video) use lightbox for quick preview
- Three.js r147 used for stable 3D loader compatibility (last version with legacy `/examples/js/` structure)
- Removed unsupported formats: FBX and 3DS (loaders not available in Three.js r147)

## [1.7.13] - 2025-10-29

### Changed
- **Version Management**: Unified version display across all interfaces
  - Web Interface: Dashboard and login now show dynamic version from `__version__`
  - CLI: `--version` flag now shows dynamic version from `__version__`
  - Desktop GUI: Now imports version from main package instead of hardcoded
  - API: Already using dynamic version (no changes needed)
  - All interfaces now consistently display version 1.7.13

### Fixed
- Removed hardcoded version strings from templates and interface files
- Web dashboard was showing v1.5.5 (now shows v1.7.13)
- Web login was showing v1.0.7 (now shows v1.7.13)
- CLI was showing v0.1.0 (now shows v1.7.13)
- Desktop GUI was using v0.1.0 (now shows v1.7.13)

## [1.7.12] - 2025-10-29

### Fixed - CRITICAL
- **Desktop GUI**: Synchronized all files with actively developed version
  - Added missing `assets/` folder with GUI assets
  - Updated `__init__.py`, `graphml_export_dialog.py`, `i18n.py`
  - Updated `media_manager_advanced.py`, `us_dialog_extended.py`
  - All Desktop GUI features now match latest development version

### Impact
- Desktop GUI was missing critical files (assets folder and 5+ Python files)
- Systematic comparison revealed archive_local contained most complete versions
- All interface directories (Web, CLI, Desktop GUI) now fully synchronized
- Package now contains complete, up-to-date code for all interfaces

## [1.7.10] - 2025-10-29

### Fixed - CRITICAL
- **All Interfaces**: Synchronized all interface code with actively developed versions
  - **Web Interface**: Fixed import statements in all route files
    - Fixed `em_node_config_routes.py` imports to use package-qualified paths
    - Fixed `excel_import_routes.py`, `harris_creator_routes.py`, `pyarchinit_import_export_routes.py`
    - Removed all `sys.path.append('..')` statements
    - All imports now use full package paths: `from pyarchinit_mini.web_interface.* import`
  - **Desktop GUI**: Updated to latest version from external development
    - Copied `main_window.py`, `gui_app.py`, `excel_import_dialog.py`, `pyarchinit_import_export_dialog.py`
    - Fixed import statements for package compatibility
    - Added missing PyArchInit import/export dialog and Excel import dialog features
  - **CLI Interface**: Synchronized with external development version
    - Ensured all features are up to date
  - **Web Interface app.py**: Copied and updated from external development version
    - Added `__version__` import and injection in context processor
    - All template contexts now have access to current version number

### Impact - CRITICAL FIX
- Version 1.7.9 had import errors preventing web server from starting
- This release fixes all import issues and ensures all interfaces work correctly
- All interfaces now use the actively developed code from external directories
- Package structure is now correctly configured for pip installation

### Technical Details
- The external development directories (`archive_local/web_interface`, `archive_local/desktop_gui`, `archive_local/cli_interface`) contained the most up-to-date code
- Previous versions were mistakenly using older code from the package directory
- This release properly synchronizes all package code with external development versions
- Import statements have been corrected to work within the installed package context

## [1.7.9] - 2025-10-29

### Fixed - CRITICAL
- **Web Interface**: Restored missing features from external development version
  - **RESTORED 4 Missing Route Files**:
    - `pyarchinit_import_export_routes.py` - PyArchInit legacy format import/export
    - `harris_creator_routes.py` - Interactive Harris Matrix creator interface
    - `excel_import_routes.py` - Excel batch import functionality
    - `em_node_config_routes.py` - Extended Matrix node configuration
  - **Enhanced US Form** with additional fields:
    - `tipo_documento` field with file type selection
    - `documento_file` field for file upload
    - Extended `unita_tipo` choices (VSF, SF, CON, USD, USVA, USVB, USVC, DOC, TU, property, Combiner, Extractor)
    - Changed `us` field from IntegerField to StringField for alphanumeric support
  - **Additional Service Imports**:
    - `RelationshipSyncService` for stratigraphic relationship management
    - `DatazioneService` for chronological data handling

### Impact - CRITICAL FIX
- Version 1.7.8 was published with incomplete web_interface code
- This release restores all missing functionality that was in active development
- Users upgrading from 1.7.7 or earlier now get the complete feature set
- Fixes missing routes that would cause 404 errors for PyArchInit import, Harris Creator, Excel Import

### Note
- The external `/web_interface` directory contained the actively developed code
- Version 1.7.8 mistakenly used the older package version
- This release properly integrates the external development code into the package

## [1.7.8] - 2025-10-29

### Fixed
- **Version Consistency Across All Interfaces**: Unified version display across all interfaces
  - **API**: Now uses `__version__` from main package instead of hardcoded "0.1.0"
  - **CLI**: Updated version display from hardcoded "v1.2.12" to dynamic `v{__version__}`
  - **Desktop GUI**: Now imports and uses `__version__` from main package
  - **Web Interface**: Already using dynamic version (from 1.7.7)
  - All interfaces now display correct synchronized version number

### Changed
- **Repository Cleanup**: Removed duplicate development directories
  - Moved old package versions (1.2.14, 1.4.0, 1.6.1) to `archive_local/`
  - Removed duplicate `web_interface/`, `cli_interface/`, `desktop_gui/` directories
  - Removed test directories: `test_data/`, `test_graphml/`, `examples/`
  - Updated `.gitignore` to exclude archived and development files

### Added
- **Documentation**: Added comprehensive tutorial documentation
  - Installation tutorial with step-by-step setup guide
  - Web interface tutorial with screenshots
  - Desktop GUI tutorial
  - Tutorial index page in ReadTheDocs

### Impact
- All interfaces (API, CLI, Desktop GUI, Web) now display version 1.7.8
- Cleaner repository structure with only necessary files
- Better documentation for new users
- Reduced package confusion from duplicate directories

## [1.7.7] - 2025-10-29

### Fixed
- **Database Schema i18n**: Added missing internationalization columns to sample databases
  - **Site table**: Added `definizione_sito_en`, `descrizione_en` (2 columns)
  - **US table**: Added 15 i18n/document columns (`d_stratigrafica_en`, `d_interpretativa_en`, `descrizione_en`, `interpretazione_en`, `formazione_en`, `stato_di_conservazione_en`, `colore_en`, `consistenza_en`, `struttura_en`, `inclusi_en`, `campioni_en`, `documentazione_en`, `osservazioni_en`, `tipo_documento`, `file_path`)
  - **Inventario table**: Added 9 i18n columns (`tipo_reperto_en`, `criterio_schedatura_en`, `definizione_en`, `descrizione_en`, `stato_conservazione_en`, `elementi_reperto_en`, `corpo_ceramico_en`, `rivestimento_en`, `tipo_contenitore_en`)
  - Fixed all `OperationalError: no such column` errors on dashboard load
  - All sample databases now have complete schema with full i18n support

### Impact
- Dashboard loads correctly without SQL errors
- All main tables (Sites, US, Inventory) support bilingual content
- Full bilingual (IT/EN) support now functional in web interface
- Resolves issues for users in multilingual archaeological projects
- Total: 26 new columns added across all sample databases

## [1.7.6] - 2025-10-29

### Fixed
- **Sample Databases Authentication**: Added admin user to all sample databases
  - Created `users` table in `pyarchinit_mini.db`
  - Created `users` table in `pyarchinit_mini_sample.db`
  - All databases now include admin user (username: `admin`, password: `admin`)
  - Users can now log in to web interface without manual database setup

### Impact
- Fresh installs can immediately access web interface with admin credentials
- No need to manually create admin user after installation

## [1.7.5] - 2025-10-29

### Fixed
- **Critical Code Restoration**: Restored complete 1.7.0 code base with all features
  - Version 1.7.4 published with incomplete code (missing database_creator, harris features)
  - Restored from git commit 5a3fbf0 which contains all 1.7.0 features
  - All features now present: database creation, harris matrix, networks, extended matrix
- **Version String Alignment**: Corrected `__version__` in `__init__.py` to match package version
  - All version identifiers now consistently report correct version
  - Login template now dynamically displays version from `__version__`

### Added
- **Dynamic Version Display**: Login template now uses `{{ version }}` variable
  - Added `__version__` import in web interface app.py
  - Modified context_processor to inject version into all templates
  - No more hardcoded version strings in templates

### Documentation
- Interactive Tutorials with Screenshots remain from 1.7.4
- Tutorial database and screenshot automation tools available

## [1.7.4] - 2025-10-29

⚠️ **This version was published with incomplete code. Use 1.7.5 instead.**

### Issues
- Published with code from version 1.7.2 instead of 1.7.0
- Missing: database_creator, enhanced harris matrix features, network exporters

## [1.7.3] - 2025-10-29

### Added
- **ReadTheDocs Multiple Formats**: Enabled PDF, EPUB, and HTMLZip generation on ReadTheDocs
  - PDF output with optimized LaTeX configuration
  - EPUB output with metadata and cover image
  - HTMLZip for offline documentation access
  - Updated `.readthedocs.yaml` to enable all formats
  - Added EPUB configuration in `docs/conf.py`

### Documentation
- Documentation now available in 4 formats on ReadTheDocs:
  - HTML (online reading)
  - PDF (printable/offline)
  - EPUB (e-readers)
  - HTMLZip (offline archive)

## [1.7.2] - 2025-10-29

### Changed
- **Documentation: GraphML Export Clarification** - Complete rewrite of technical documentation
  - Clarified that **Pure NetworkX is the DEFAULT export method** (no Graphviz required)
  - Graphviz is now correctly documented as **OPTIONAL** (only for DOT file generation)
  - Added clear comparison table between Pure NetworkX vs Graphviz export methods
  - Updated all code examples to show both export approaches
  - Removed misleading statements that suggested Graphviz was required
  - Added troubleshooting section for both export methods
  - Updated README.md to reflect that Graphviz is optional
  - Technical guide now at: `docs/features/graphml-export-technical.rst`

### Documentation Improvements
- Restructured GraphML export documentation for clarity
- Added "When to Use" sections for each export method
- Improved CLI and API usage examples
- Added comprehensive comparison table
- Enhanced troubleshooting guide with clear solutions

## [1.7.1] - 2025-10-29

### Changed
- **Documentation Links**: Updated all README documentation links to point to ReadTheDocs
  - Excel Import Guide → https://pyarchinit-mini.readthedocs.io/en/latest/features/harris_matrix_import.html
  - Extended Matrix Export → https://pyarchinit-mini.readthedocs.io/en/latest/features/graphml-export-technical.html
  - DOC File Upload → https://pyarchinit-mini.readthedocs.io/en/latest/features/media_management.html
  - EM Node Type Management → https://pyarchinit-mini.readthedocs.io/en/latest/features/extended-matrix-framework.html
  - CHANGELOG → https://pyarchinit-mini.readthedocs.io/en/latest/development/changelog.html
  - Quick Start → https://pyarchinit-mini.readthedocs.io/en/latest/installation/quickstart.html
  - Contributing Guide → https://pyarchinit-mini.readthedocs.io/en/latest/development/contributing.html
- Removed broken links to non-existent documentation files
- Improved documentation accessibility for PyPI users

### Fixed
- Removed invalid documentation file references
- Updated documentation section with centralized ReadTheDocs links

## [1.6.1] - 2025-10-28

### Added
- **Excel Import Web GUI**: Complete integration with dual format support
  - Harris Matrix Template format (sheet-based: NODES + RELATIONSHIPS)
  - Extended Matrix Parser format (inline with relationship columns)
  - Radio button format selection
  - Site name validation
  - Optional GraphML generation
  - Success/error messages with statistics
- **Documentation**: Comprehensive Excel import guide (500+ lines)
  - `docs/EXCEL_IMPORT_GUIDE.md` - User guide
  - `docs/EXCEL_IMPORT_BUG_FIXES.md` - Technical bug fixes
  - `docs/EXCEL_IMPORT_INTEGRATION_SUMMARY.md` - Session summary
- **Italian Relationships**: Full support for lowercase Italian relationship names
- **Database Consistency**: Unified database path across Web GUI, Desktop GUI, and CLI

### Fixed
- **CRITICAL: Database Schema**: Fixed `id_us` field type from `VARCHAR(100)` to `INTEGER AUTOINCREMENT`
  - Old databases created with v1.6.0 or earlier may have incorrect schema
  - Migration instructions provided in documentation
- **Date Type Handling**: Fixed SQLite date field type errors (None instead of .isoformat())
- **Desktop GUI**: Updated to use consistent database connection via `db_manager.connection`
- **Italian Relationships**: Added lowercase variants ("anteriore a", "copre", "coperto da", etc.)

### Changed
- **Web GUI Routes**: Registered `excel_import_bp` blueprint with CSRF exemption
- **Desktop GUI**: Modified `excel_import_dialog.py` to pass `db_connection` parameter

### Testing
- ✅ Harris Template: 20 US + 24 relationships imported successfully
- ✅ Extended Matrix: 5 US + 6 relationships imported successfully
- ✅ Metro C Real Data: 65 US + 658 relationships imported successfully
- ✅ All data visible immediately in all interfaces

### Migration Note
**IMPORTANT**: Users upgrading from v1.6.0 or earlier must recreate or migrate their database due to schema changes. See `docs/EXCEL_IMPORT_BUG_FIXES.md` for detailed migration instructions.

### Files Modified
- `web_interface/excel_import_routes.py` - New file
- `web_interface/templates/excel_import/index.html` - New file
- `web_interface/app.py` - Blueprint registration
- `web_interface/templates/base.html` - Menu link
- `desktop_gui/excel_import_dialog.py` - Database consistency fix
- `pyarchinit_mini/services/extended_matrix_excel_parser.py` - Bug fixes
- `pyarchinit_mini/cli/harris_import.py` - Bug fixes
- `README.md` - Feature documentation
- `docs/index.rst` - What's New section
- `pyproject.toml` - Version 1.6.1
- `docs/conf.py` - Version 1.6.1

---

## [1.5.8] - 2025-10-27
## [1.5.9] - 2025-10-27

### Fixed
- **Italian Translation**: Corrected "Errore export PDF" → "Esporta PDF" for Export PDF button
- **English Translations**: Added missing translations for Configuration menu and Thesaurus ICCD

### Added
- **README**: Updated with v1.5.8 features (Periodization & Thesaurus Management interfaces)

### Technical
- Files modified:
  - `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po` - Fixed PDF export button translation
  - `pyarchinit_mini/translations/en/LC_MESSAGES/messages.po` - Added Configuration and Thesaurus ICCD translations
  - `pyarchinit_mini/translations/*/LC_MESSAGES/messages.mo` - Recompiled translation catalogs
  - `README.md` - Added Periodization & Thesaurus Management section
  - `pyproject.toml` - Version 1.5.9

### Impact
- Correct button labels in Italian interface
- Complete internationalization support for new features
- Updated documentation reflects latest capabilities


### Added
- **Periodizzazione Management Interface**
  - Complete CRUD web interface for managing archaeological dating periods
  - List view displaying all datazioni with pagination support
  - Create form with fields: nome_datazione, fascia_cronologica, descrizione
  - Edit functionality for updating existing dating periods
  - Delete functionality with confirmation dialog
  - Integrated in navigation menu under "Configuration" section

- **Thesaurus ICCD Management Interface**
  - Complete CRUD web interface for ICCD controlled vocabularies
  - Two-step selection: choose table, then field
  - Dynamic field dropdown based on selected table
  - Display predefined ICCD values (read-only) with "ICCD" badge
  - Create, edit, and delete custom vocabulary values
  - Inline editing with JavaScript for quick updates
  - Visual distinction between predefined and custom values (gray background for ICCD)
  - Help documentation explaining ICCD standard compliance

- **US Form Thesaurus Integration**
  - `definizione_stratigrafica`: NEW field added as SelectField with thesaurus values
  - `formazione`: Converted from hardcoded to dynamic thesaurus-driven SelectField
  - `colore`: Converted from StringField to SelectField with thesaurus values
  - `consistenza`: Converted from hardcoded to dynamic thesaurus-driven SelectField
  - All fields populated via `ThesaurusService.get_field_values()`
  - Works in both `/us/create` and `/us/<us_id>/edit` routes

- **Navigation Updates**
  - New "Configuration" section in dropdown menu and sidebar
  - Links to Periodizzazione and Thesaurus ICCD interfaces
  - Italian translations: "Configurazione", "Periodizzazione", "Thesaurus ICCD"

### Changed
- **Thesaurus Routes**
  - `/thesaurus/<field_id>/edit` and `/thesaurus/<field_id>/delete` now accept string IDs
  - Protection for predefined ICCD values (cannot be modified or deleted)
  - Warning messages when attempting to modify read-only values

- **Template Improvements**
  - Thesaurus list template with conditional rendering for read-only values
  - Visual indicators (badges, locked icons) for ICCD predefined entries
  - Help cards with usage instructions in all new interfaces

### Fixed
- **CSRF Protection**
  - Added CSRF tokens to periodizzazione create/edit forms
  - Added CSRF tokens to thesaurus create/edit/delete forms
  - Fixed inline JavaScript edit function to include CSRF token

- **Thesaurus State Management**
  - Fixed table/field selection losing state on page reload
  - Replaced `form.submit()` with JavaScript URL parameter management
  - Maintains query parameters (?table=x&field=y) across interactions

- **Predefined Values Handling**
  - Fixed "invalid literal for int() with base 10: 'predefined_0'" error
  - Proper handling of string IDs for predefined vocabulary entries
  - Routes now check for 'predefined_' prefix before attempting integer conversion

### Technical
- Files modified:
  - `web_interface/app.py` - Added periodizzazione routes (2478-2594), thesaurus routes (2596-2717), updated USForm with thesaurus fields
  - `web_interface/templates/periodizzazione/list.html` - NEW: List interface for datazioni
  - `web_interface/templates/periodizzazione/form.html` - NEW: Create/edit form for datazioni
  - `web_interface/templates/thesaurus/list.html` - NEW: ICCD thesaurus management interface
  - `web_interface/templates/us/form.html` - Updated definizione_stratigrafica, formazione, colore, consistenza fields
  - `web_interface/templates/base.html` - Added Configuration section to navigation
  - `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po` - Added Italian translations
  - `pyproject.toml` - Version 1.5.8

### User Experience
- Users can now manage archaeological dating periods via web interface
- ICCD controlled vocabularies fully manageable with clear distinction between standard and custom values
- US forms now use standardized thesaurus values for consistency
- Read-only protection ensures ICCD standard compliance
- Intuitive two-step selection (table → field) for thesaurus management
- Visual feedback (badges, colors) for different value types

### Impact
- Complete web GUI for configuration management
- ICCD standards compliance with user-friendly interface
- Enhanced data quality through controlled vocabularies
- Foundation for future thesaurus expansion to other forms
- Consistent terminology across archaeological documentation

## [1.5.7] - 2025-10-27

### Added
- **Web GUI Combobox Integration for Datazioni**
  - `datazione` field in US form now uses SelectField with database-driven choices
  - Dynamic dropdown populated from `datazioni_table` via `DatazioneService`
  - Choices displayed in format: "Nome Datazione (Fascia Cronologica)"
  - Default option: "-- Seleziona Datazione --"
  - Works in both `/us/create` and `/us/<us_id>/edit` routes

- **Italian Translation for Chronology Fields**
  - "Initial Period" → "Periodo Iniziale"
  - "Initial Phase" → "Fase Iniziale"
  - "Final Period" → "Periodo Finale"
  - "Final Phase" → "Fase Finale"
  - Translations added to `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po`

### Changed
- **US Form Field Type Updates**
  - `datazione`: Changed from StringField to SelectField (dropdown with 36 Italian periods)
  - `periodo_iniziale`: Changed from SelectField to StringField (removed 40+ hardcoded choices)
  - `periodo_finale`: Changed from SelectField to StringField (removed 40+ hardcoded choices)
  - `fase_iniziale`: Remains StringField (flexible text entry)
  - `fase_finale`: Remains StringField (flexible text entry)

- **Service Integration**
  - `DatazioneService` initialized at Flask app startup
  - `get_datazioni_choices()` returns formatted list of dicts: `[{'value': 'nome', 'label': 'Nome (Fascia)'}]`
  - Fixed dict access syntax in `get_datazioni_choices()` to use `d['nome_datazione']` instead of `d.nome_datazione`

- **Bootstrap 5 CSS Classes**
  - `datazione`: Uses `form-select` class for dropdown styling
  - `periodo_iniziale`, `periodo_finale`, `fase_iniziale`, `fase_finale`: Use `form-control` class for text input styling

### Fixed
- **Session Management**
  - Fixed AttributeError: 'dict' object has no attribute 'nome_datazione'
  - All DatazioneService methods return dicts instead of ORM objects to prevent detached instance errors

### Technical
- Files modified:
  - `web_interface/app.py` - Added DatazioneService import, updated USForm fields, populated choices in create/edit routes
  - `web_interface/templates/us/form.html` - Updated field rendering with correct CSS classes
  - `pyarchinit_mini/services/datazione_service.py` - Fixed dict access in get_datazioni_choices()
  - `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po` - Added Italian translations
  - `README.md` - Added v1.5.7 release notes
  - `docs/index.rst` - Added v1.5.7 version documentation
  - `pyproject.toml` - Version 1.5.7

### User Experience
- Users can now select standardized datazioni from dropdown with 36 Italian archaeological periods
- Free-text entry for periodo/fase fields maintains flexibility for chronological data
- Full Italian language support in web interface
- Consistent dropdown behavior on both create and edit forms

### Next Steps (v1.6.0)
- Desktop GUI combobox integration for datazione field
- Parser synchronization with datazioni table
- Import/export updates for datazioni support

### Impact
- Web interface now provides standardized chronological dating selection
- Maintains flexibility with free-text periodo/fase fields
- Foundation completed for Desktop GUI integration
- Consistent user experience across create and edit workflows

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
