# API Index

## Classes

| Name | File | Methods | Description |
|------|------|---------|-------------|
| BaseDialog | desktop_gui/dialogs.py | 5 | Base class for dialog windows |
| BaseModel | pyarchinit_mini/models/base.py | 2 | Base model class with common fields and methods |
| BaseSchema | pyarchinit_mini/api/schemas.py | 0 | Base schema with common fields |
| BaseValidator | pyarchinit_mini/utils/validators.py | 3 | Base validator class |
| ChronologicalSequenceDialog | desktop_gui/us_dialog_extended.py | 12 | Dialog for displaying chronological sequence |
| Config | pyarchinit_mini/api/schemas.py | 0 | The **Config** class defines configuration options for Pydantic models, enabling advanced behavior c |
| Config | pyarchinit_mini/api/schemas.py | 0 | The **Config** class defines pagination parameters for data retrieval, specifying the current page,  |
| ConfigurationError | pyarchinit_mini/exceptions.py | 0 | Configuration errors |
| ConfigurationError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when configuration is invalid |
| ConnectionError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when database connection fails |
| DatabaseConfigDialog | desktop_gui/dialogs.py | 11 | Dialog for database configuration |
| DatabaseConnection | pyarchinit_mini/database/connection.py | 11 | Manages database connections for both PostgreSQL and SQLite |
| DatabaseError | pyarchinit_mini/exceptions.py | 0 | Database related errors |
| DatabaseError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when database operations fail |
| DatabaseManager | pyarchinit_mini/database/manager.py | 16 | High-level database manager providing CRUD operations |
| DatabaseMigrations | pyarchinit_mini/database/migrations.py | 7 | Handle database schema migrations |
| DatabaseSchema | pyarchinit_mini/database/schemas.py | 9 | Utilities for database schema management and migrations |
| Documentation | pyarchinit_mini/models/media.py | 1 | Documentation files and reports |
| DocumentationService | pyarchinit_mini/services/media_service.py | 8 | Service class for documentation operations |
| DuplicateRecordError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when trying to create a duplicate record |
| EnhancedHarrisMatrixVisualizer | pyarchinit_mini/harris_matrix/enhanced_visualizer.py | 10 | Enhanced Harris Matrix visualizer using Graphviz for hierarchical orthogonal layout |
| ExtendedInventarioDialog | desktop_gui/inventario_dialog_extended.py | 26 | Extended Inventory Dialog with all fields from PyArchInit plugin |
| ExtendedUSDialog | desktop_gui/us_dialog_extended.py | 36 | Extended US dialog with multiple tabs for complete archaeological recording |
| HarrisMatrix | pyarchinit_mini/models/harris_matrix.py | 1 | Harris Matrix relationships between stratigraphic units |
| HarrisMatrixDialog | desktop_gui/dialogs.py | 17 | Dialog for generating and viewing Harris Matrix |
| HarrisMatrixEditor | desktop_gui/harris_matrix_editor.py | 32 | Advanced Harris Matrix editor with relationship management and validation |
| HarrisMatrixGenerator | pyarchinit_mini/harris_matrix/matrix_generator.py | 9 | Generates Harris Matrix from stratigraphic relationships |
| InventarioBase | pyarchinit_mini/api/schemas.py | 1 | Base inventory schema |
| InventarioCreate | pyarchinit_mini/api/schemas.py | 0 | Schema for creating inventory item |
| InventarioDTO | pyarchinit_mini/dto/inventario_dto.py | 3 | Data Transfer Object for Inventario (Material Inventory) data |
| InventarioDialog | desktop_gui/dialogs.py | 4 | Dialog for creating/editing inventory items |
| InventarioForm | web_interface/app.py | 0 | The **InventarioForm** class is a Flask-WTF form designed for managing and submitting inventory reco |
| InventarioMateriali | pyarchinit_mini/models/inventario_materiali.py | 3 | Material inventory model |
| InventarioResponse | pyarchinit_mini/api/schemas.py | 0 | Schema for inventory response |
| InventarioService | pyarchinit_mini/services/inventario_service.py | 19 | Service class for inventory operations |
| InventarioUpdate | pyarchinit_mini/api/schemas.py | 0 | Schema for updating inventory item |
| InventarioValidator | pyarchinit_mini/utils/validators.py | 1 | Validator for Inventario Materiali model data |
| MatrixVisualizer | pyarchinit_mini/harris_matrix/matrix_visualizer.py | 5 | Visualizes Harris Matrix using different rendering methods |
| Media | pyarchinit_mini/models/media.py | 3 | Media files (images, documents, videos) linked to archaeological records |
| MediaHandler | pyarchinit_mini/media_manager/media_handler.py | 11 | Handles media file operations, storage, and organization |
| MediaManagerDialog | desktop_gui/dialogs.py | 4 | Dialog for media management |
| MediaService | pyarchinit_mini/services/media_service.py | 17 | Service class for media operations |
| MediaThumb | pyarchinit_mini/models/media.py | 1 | Thumbnails for media files |
| MediaUploadForm | web_interface/app.py | 0 | The **MediaUploadForm** class is a Flask-WTF form designed to facilitate the upload of media files r |
| NumberedCanvasFinds | pyarchinit_mini/pdf_export/pyarchinit_finds_template.py | 4 | Canvas with page numbering for finds sheets |
| PDFExportDialog | desktop_gui/dialogs.py | 5 | Dialog for PDF export |
| PDFGenerator | pyarchinit_mini/pdf_export/pdf_generator.py | 11 | Generate PDF reports for archaeological data |
| PaginatedResponse | pyarchinit_mini/api/schemas.py | 0 | Paginated response wrapper |
| PaginationParams | pyarchinit_mini/api/schemas.py | 0 | Pagination parameters |
| Period | pyarchinit_mini/models/harris_matrix.py | 1 | Archaeological periods and phases |
| PeriodizationDialog | desktop_gui/us_dialog_extended.py | 8 | Dialog for detailed periodization management |
| Periodizzazione | pyarchinit_mini/models/harris_matrix.py | 2 | Periodization assignments for archaeological contexts |
| PeriodizzazioneService | pyarchinit_mini/services/periodizzazione_service.py | 21 | Service class for periodization operations |
| PermissionError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when user lacks required permissions |
| PostgreSQLInstaller | pyarchinit_mini/database/postgres_installer.py | 11 | Manages PostgreSQL installation on different platforms |
| PostgreSQLInstallerDialog | desktop_gui/postgres_installer_dialog.py | 11 | Dialog for PostgreSQL installation and setup |
| PyArchInitCLI | cli_interface/cli_app.py | 14 | Interactive CLI for PyArchInit-Mini |
| PyArchInitError | pyarchinit_mini/exceptions.py | 0 | Base exception for PyArchInit-Mini |
| PyArchInitFindsTemplate | pyarchinit_mini/pdf_export/pyarchinit_finds_template.py | 2 | PyArchInit finds template manager |
| PyArchInitGUI | desktop_gui/main_window.py | 52 | Main GUI application for PyArchInit-Mini |
| PyArchInitInventoryTemplate | pyarchinit_mini/pdf_export/pyarchinit_inventory_template.py | 4 | Authentic PyArchInit inventory template following the original design |
| PyArchInitMatrixVisualizer | pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py | 10 | Harris Matrix visualizer that replicates PyArchInit plugin behavior |
| PyArchInitMiniError | pyarchinit_mini/utils/exceptions.py | 0 | Base exception class for PyArchInit-Mini |
| RecordNotFoundError | pyarchinit_mini/database/manager.py | 0 | Record not found error |
| RecordNotFoundError | pyarchinit_mini/utils/exceptions.py | 0 | Raised when a requested record is not found |
| RelationshipDialog | desktop_gui/us_dialog_extended.py | 4 | Simple dialog for adding stratigraphic relationships |
| SampleDataGenerator | scripts/populate_sample_data.py | 9 | Generator for archaeological sample data |
| ServiceError | pyarchinit_mini/exceptions.py | 0 | Service layer errors |
| SingleFindsSheet | pyarchinit_mini/pdf_export/pyarchinit_finds_template.py | 4 | Single finds sheet based on PyArchInit original |
| Site | pyarchinit_mini/models/site.py | 2 | Archaeological site model |
| SiteBase | pyarchinit_mini/api/schemas.py | 0 | Base site schema |
| SiteCreate | pyarchinit_mini/api/schemas.py | 0 | Schema for creating a site |
| SiteDTO | pyarchinit_mini/dto/site_dto.py | 3 | Data Transfer Object for Site data |
| SiteDialog | desktop_gui/dialogs.py | 16 | Dialog for creating/editing sites with media support |
| SiteForm | web_interface/app.py | 0 | The **SiteForm** class is a Flask-WTF form designed for capturing and validating information about a |
| SiteResponse | pyarchinit_mini/api/schemas.py | 0 | Schema for site response |
| SiteService | pyarchinit_mini/services/site_service.py | 18 | Service class for site operations |
| SiteUpdate | pyarchinit_mini/api/schemas.py | 0 | Schema for updating a site |
| SiteValidator | pyarchinit_mini/utils/validators.py | 1 | Validator for Site model data |
| StatisticsDialog | desktop_gui/dialogs.py | 3 | Dialog for viewing statistics |
| ThesaurusCategory | pyarchinit_mini/models/thesaurus.py | 1 | Categories for organizing thesaurus entries |
| ThesaurusDialog | desktop_gui/thesaurus_dialog.py | 17 | Dialog for managing thesaurus and controlled vocabularies |
| ThesaurusField | pyarchinit_mini/models/thesaurus.py | 2 | Field-specific thesaurus entries |
| ThesaurusService | pyarchinit_mini/services/thesaurus_service.py | 8 | Service for managing thesaurus and controlled vocabularies |
| ThesaurusSigle | pyarchinit_mini/models/thesaurus.py | 2 | Thesaurus for controlled vocabularies and abbreviations |
| US | pyarchinit_mini/models/us.py | 3 | Stratigraphic Unit model |
| USBase | pyarchinit_mini/api/schemas.py | 0 | Base US schema |
| USCreate | pyarchinit_mini/api/schemas.py | 0 | Schema for creating a US |
| USDTO | pyarchinit_mini/dto/us_dto.py | 3 | Data Transfer Object for US (Stratigraphic Unit) data |
| USDialog | desktop_gui/dialogs.py | 4 | Dialog for creating/editing US |
| USForm | web_interface/app.py | 0 | The **USForm** class defines a data entry form for recording archaeological stratigraphic unit (US)  |
| USRelationships | pyarchinit_mini/models/harris_matrix.py | 1 | Detailed stratigraphic relationships between US |
| USResponse | pyarchinit_mini/api/schemas.py | 0 | Schema for US response |
| USService | pyarchinit_mini/services/us_service.py | 15 | Service class for US operations |
| USUpdate | pyarchinit_mini/api/schemas.py | 0 | Schema for updating a US |
| USValidator | pyarchinit_mini/utils/validators.py | 1 | Validator for US (Stratigraphic Unit) model data |
| ValidationError | pyarchinit_mini/exceptions.py | 0 | Data validation errors |
| ValidationError | pyarchinit_mini/utils/exceptions.py | 1 | Raised when data validation fails |


## Functions

| Name | File | Parameters | Returns |
|------|------|------------|---------|
| api_sites | web_interface/app.py | 0 | None |
| check_dependencies | desktop_gui/gui_app.py | 0 | None |
| close_database | pyarchinit_mini/api/dependencies.py | 0 | None |
| create_app | web_interface/app.py | 0 | None |
| create_app | pyarchinit_mini/api/__init__.py | 1 | FastAPI |
| create_inventario | web_interface/app.py | 0 | None |
| create_inventario_item | pyarchinit_mini/api/inventario.py | 2 | None |
| create_sample_data | examples/interface_demo.py | 0 | None |
| create_sample_data | scripts/populate_simple_data.py | 1 | None |
| create_site | web_interface/app.py | 0 | None |
| create_site | pyarchinit_mini/api/site.py | 2 | None |
| create_us | web_interface/app.py | 0 | None |
| create_us | pyarchinit_mini/api/us.py | 2 | None |
| db_manager | tests/conftest.py | 1 | None |
| delete_inventario_item | pyarchinit_mini/api/inventario.py | 2 | None |
| delete_site | pyarchinit_mini/api/site.py | 2 | None |
| delete_us | pyarchinit_mini/api/us.py | 2 | None |
| demo_api_server | examples/interface_demo.py | 0 | None |
| demo_cli_interface | examples/interface_demo.py | 0 | None |
| demo_desktop_gui | examples/interface_demo.py | 0 | None |
| demo_python_library | examples/interface_demo.py | 0 | None |
| demo_web_interface | examples/interface_demo.py | 0 | None |
| export_site_pdf | web_interface/app.py | 1 | None |
| get_attr | desktop_gui/dialogs.py | 3 | None |
| get_countries | pyarchinit_mini/api/site.py | 1 | None |
| get_database_connection | pyarchinit_mini/api/dependencies.py | 0 | DatabaseConnection |
| get_database_manager | pyarchinit_mini/api/dependencies.py | 1 | DatabaseManager |
| get_inventario_item | pyarchinit_mini/api/inventario.py | 2 | None |
| get_inventario_list | pyarchinit_mini/api/inventario.py | 5 | None |
| get_inventario_service | pyarchinit_mini/api/dependencies.py | 1 | InventarioService |
| get_municipalities | pyarchinit_mini/api/site.py | 3 | None |
| get_regions | pyarchinit_mini/api/site.py | 2 | None |
| get_site | pyarchinit_mini/api/site.py | 2 | None |
| get_site_by_name | pyarchinit_mini/api/site.py | 2 | None |
| get_site_service | pyarchinit_mini/api/dependencies.py | 1 | SiteService |
| get_site_stats | pyarchinit_mini/api/site.py | 2 | None |
| get_sites | pyarchinit_mini/api/site.py | 7 | None |
| get_us | pyarchinit_mini/api/us.py | 2 | None |
| get_us_list | pyarchinit_mini/api/us.py | 5 | None |
| get_us_service | pyarchinit_mini/api/dependencies.py | 1 | USService |
| harris_matrix | web_interface/app.py | 1 | None |
| health_check | pyarchinit_mini/api/__init__.py | 0 | None |
| index | web_interface/app.py | 0 | None |
| init_database | pyarchinit_mini/api/dependencies.py | 1 | None |
| inventario_list | web_interface/app.py | 0 | None |
| inventario_service | tests/conftest.py | 1 | None |
| load_sample_database | scripts/load_sample_as_main.py | 0 | None |
| main | run_gui.py | 0 | None |
| main | launch_with_sample_data.py | 0 | None |
| main | example_usage.py | 0 | None |
| main | main.py | 0 | None |
| main | test_interfaces.py | 0 | None |
| main | test_gui_with_data.py | 0 | None |
| main | migrate_database.py | 0 | None |
| main | test_dialogs.py | 0 | None |
| main | cli_interface/cli_app.py | 2 | None |
| main | desktop_gui/gui_app.py | 0 | None |
| main | examples/interface_demo.py | 0 | None |
| main | scripts/populate_sample_data.py | 0 | None |
| main | scripts/update_sample_relationships.py | 0 | None |
| on_postgres_installed | desktop_gui/main_window.py | 1 | None |
| print_banner | examples/interface_demo.py | 1 | None |
| root | pyarchinit_mini/api/__init__.py | 0 | None |
| run_api | launch_with_sample_data.py | 0 | None |
| safe_str | pyarchinit_mini/pdf_export/pyarchinit_inventory_template.py | 1 | None |
| safe_str | pyarchinit_mini/pdf_export/pdf_generator.py | 1 | None |
| sample_inventario_data | tests/conftest.py | 0 | None |
| sample_site_data | tests/conftest.py | 0 | None |
| sample_us_data | tests/conftest.py | 0 | None |
| save_changes | desktop_gui/harris_matrix_editor.py | 0 | None |
| set_sqlite_pragma | pyarchinit_mini/database/connection.py | 2 | None |
| site_service | tests/conftest.py | 1 | None |
| sites_list | web_interface/app.py | 0 | None |
| temp_db | tests/conftest.py | 0 | None |
| test_all_improvements | test_all_improvements.py | 0 | None |
| test_all_interfaces | final_test.py | 0 | None |
| test_api_server | test_interfaces.py | 0 | None |
| test_cascade_deletion | scripts/test_cascade_delete.py | 0 | None |
| test_cli_interface | test_interfaces.py | 0 | None |
| test_component | test_interfaces.py | 2 | None |
| test_count_sites | tests/unit/test_site_service.py | 2 | None |
| test_create_site_duplicate_name | tests/unit/test_site_service.py | 2 | None |
| test_create_site_invalid_data | tests/unit/test_site_service.py | 1 | None |
| test_create_site_success | tests/unit/test_site_service.py | 2 | None |
| test_database_core | test_interfaces.py | 0 | None |
| test_delete_site | tests/unit/test_site_service.py | 2 | None |
| test_desktop_gui | test_interfaces.py | 0 | None |
| test_dialog_creation | test_dialogs.py | 0 | None |
| test_dialog_imports | test_dialogs.py | 0 | None |
| test_final_improvements | test_final_improvements.py | 0 | None |
| test_get_all_sites | tests/unit/test_site_service.py | 1 | None |
| test_get_site_by_id | tests/unit/test_site_service.py | 2 | None |
| test_get_site_by_name | tests/unit/test_site_service.py | 2 | None |
| test_gui_with_data | test_gui_with_data.py | 0 | None |
| test_harris_gui | test_harris_gui.py | 0 | None |
| test_harris_matrix | test_interfaces.py | 0 | None |
| test_harris_matrix | test_harris_matrix.py | 0 | None |
| test_improved_harris_dialog | test_improved_harris_dialog.py | 0 | None |
| test_media_handler | test_interfaces.py | 0 | None |
| test_media_manager | test_media_manager_fix.py | 0 | None |
| test_media_manager_import | test_media_manager_simple.py | 0 | None |
| test_pdf_export | test_interfaces.py | 0 | None |
| test_services | test_interfaces.py | 0 | None |
| test_session_fixes | test_session_fixes.py | 0 | None |
| test_update_site | tests/unit/test_site_service.py | 2 | None |
| test_web_interface | test_interfaces.py | 0 | None |
| update_inventario_item | pyarchinit_mini/api/inventario.py | 3 | None |
| update_sample_relationships | scripts/update_sample_relationships.py | 0 | None |
| update_site | pyarchinit_mini/api/site.py | 3 | None |
| update_us | pyarchinit_mini/api/us.py | 3 | None |
| upload_media | web_interface/app.py | 0 | None |
| us_list | web_interface/app.py | 0 | None |
| us_service | tests/conftest.py | 1 | None |
| validate_data | pyarchinit_mini/utils/validators.py | 2 | None |
| view_site | web_interface/app.py | 1 | None |
