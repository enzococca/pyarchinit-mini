# Changelog

All notable changes to PyArchInit-Mini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
