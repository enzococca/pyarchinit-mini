# Class Diagram

## Architecture Overview

The architecture of this application follows a modular, dialog-oriented design, centered around the **PyArchInitGUI** class, which acts as the main entry point and controller for the PyArchInit-Mini GUI. Each core domain concept—such as inventory, stratigraphic units (US), site management, thesauri, and periodization—is encapsulated within its own dedicated dialog class. The use of a **BaseDialog** superclass provides a common foundation for dialog windows, encouraging code reuse and consistent UI/UX patterns across the interface. This structure aligns with the Model-View-Controller (MVC) paradigm, where dialogs serve as Views and Controllers, interfacing with underlying data models (not explicitly described here).

Key class responsibilities are clearly delineated. **ExtendedInventarioDialog** and **ExtendedUSDialog** handle complex data entry for inventory and stratigraphic units, respectively, each supporting advanced features such as media management and multi-tabbed interfaces for comprehensive archaeological recording. **ThesaurusDialog** offers controlled vocabulary management, likely ensuring data integrity across other dialogs. Database concerns are isolated in the **PostgreSQLInstallerDialog**, streamlining setup and configuration. Supporting dialogs like **RelationshipDialog**, **PeriodizationDialog**, and **ChronologicalSequenceDialog** focus on specialized tasks—managing stratigraphic relationships, periodization, and chronological sequences—facilitating modular development and maintenance.

Component interactions are orchestrated from the **PyArchInitGUI** hub, which instantiates and manages the various dialog classes based on user actions. Dialogs may communicate with each other via shared data models or signal/slot mechanisms typical in GUI frameworks, allowing for updates and consistency (e.g., changes in the thesaurus reflecting across data entry dialogs). Media support and controlled vocabularies are integrated into relevant dialogs, ensuring a cohesive user experience and robust data handling. This modular, extensible structure supports scalability and ease of future enhancements, making the codebase approachable for new developers.

```mermaid
classDiagram
    class PyArchInitGUI {
        +__init__(self)
        +setup_database(self)
        +setup_styles(self)
        +create_menu(self)
        +create_main_interface(self)
        ... +44 more methods
    }
    class ExtendedInventarioDialog {
        +__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)
        +center_window(self)
        +create_media_directory(self)
        +get_thesaurus_values(self, field_name)
        +create_identification_tab(self)
        ... +21 more methods
    }
    class ThesaurusDialog {
        +__init__(self, parent, thesaurus_service, callback)
        +center_window(self)
        +create_interface(self)
        +create_details_form(self, parent)
        +load_tables(self)
        ... +12 more methods
    }
    class PostgreSQLInstallerDialog {
        +__init__(self, parent, postgres_installer, callback)
        +center_window(self)
        +create_interface(self)
        +log_message(self, message)
        +update_progress(self, value, message)
        ... +6 more methods
    }
    class ExtendedUSDialog {
        +__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)
        +create_interface(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        +create_physical_tab(self)
        ... +31 more methods
    }
    class RelationshipDialog {
        +__init__(self, parent, us, matrix_generator, callback)
        +create_interface(self)
        +save_relationship(self)
        +cancel(self)
    }
    class PeriodizationDialog {
        +__init__(self, parent, us, periodizzazione_service, callback)
        +create_interface(self)
        +create_chronology_tab(self)
        +create_phases_tab(self)
        +create_dating_tab(self)
        ... +3 more methods
    }
    class ChronologicalSequenceDialog {
        +__init__(self, parent, site_name, us_service, periodizzazione_service)
        +create_interface(self)
        +create_timeline_tab(self)
        +create_periods_tab(self)
        +create_matrix_tab(self)
        ... +7 more methods
    }
    class BaseDialog {
        +__init__(self, parent, title, width, height)
        +center_window(self)
        +create_buttons(self, ok_text, cancel_text)
        +ok(self)
        +cancel(self)
    }
    class SiteDialog {
        +__init__(self, parent, site_service, media_service, site, callback)
        +create_media_directory(self)
        +create_form(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        ... +11 more methods
    }
    BaseDialog <|-- SiteDialog
    class USDialog {
        +__init__(self, parent, us_service, site_names, us, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- USDialog
    class InventarioDialog {
        +__init__(self, parent, inventario_service, site_names, inventario, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- InventarioDialog
    class HarrisMatrixDialog {
        +__init__(self, parent, matrix_generator, matrix_visualizer, sites)
        +create_interface(self)
        +generate_matrix(self)
        +display_statistics(self, stats)
        +display_levels(self)
        ... +2 more methods
    }
    BaseDialog <|-- HarrisMatrixDialog
    class PDFExportDialog {
        +__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)
        +create_interface(self)
        +select_output_file(self)
        +ok(self)
    }
    BaseDialog <|-- PDFExportDialog
    class DatabaseConfigDialog {
        +__init__(self, parent, callback)
        +create_interface(self)
        +on_db_type_change(self)
        +browse_sqlite_file(self)
        +test_connection(self)
        ... +2 more methods
    }
    BaseDialog <|-- DatabaseConfigDialog
    class MediaManagerDialog {
        +__init__(self, parent, media_handler)
        +create_interface(self)
        +select_file(self)
        +upload_file(self)
    }
    BaseDialog <|-- MediaManagerDialog
    class StatisticsDialog {
        +__init__(self, parent, site_service, us_service, inventario_service)
        +create_interface(self)
        +load_statistics(self)
    }
    BaseDialog <|-- StatisticsDialog
    class HarrisMatrixEditor {
        +__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)
        +create_interface(self)
        +create_control_panel(self, parent)
        +create_left_panel(self, parent)
        +create_relationships_tab(self, parent)
        ... +26 more methods
    }
    class PyArchInitCLI {
        +__init__(self, database_url)
        +show_welcome(self)
        +show_main_menu(self)
        +sites_menu(self)
        +list_sites(self)
        ... +9 more methods
    }
    class SiteForm {
    }
    FlaskForm <|-- SiteForm
    class USForm {
    }
    FlaskForm <|-- USForm
    class InventarioForm {
    }
    FlaskForm <|-- InventarioForm
    class MediaUploadForm {
    }
    FlaskForm <|-- MediaUploadForm
    class PyArchInitError {
    }
    Exception <|-- PyArchInitError
    class DatabaseError {
    }
    PyArchInitError <|-- DatabaseError
    class ValidationError {
    }
    PyArchInitError <|-- ValidationError
    class ServiceError {
    }
    PyArchInitError <|-- ServiceError
    class ConfigurationError {
    }
    PyArchInitError <|-- ConfigurationError
    class USDTO {
        +from_model(cls, us_model)
        +to_dict(self)
        +display_name(self)
    }
    class InventarioDTO {
        +from_model(cls, inventario_model)
        +to_dict(self)
        +display_name(self)
    }
    class SiteDTO {
        +from_model(cls, site_model)
        +to_dict(self)
        +display_name(self)
    }
    class DatabaseConnection {
        +__init__(self, connection_string)
        +get_session(self)
        +create_tables(self)
        +test_connection(self)
        +close(self)
        ... +3 more methods
    }
    class PostgreSQLInstaller {
        +__init__(self)
        +check_postgres_installed(self)
        +get_postgres_version(self)
        +install_postgres_macos(self)
        +install_postgres_windows(self)
        ... +4 more methods
    }
    class DatabaseManager {
        +__init__(self, connection)
        +create(self, model_class, data)
        +get_by_id(self, model_class, record_id)
        +get_by_field(self, model_class, field_name, value)
        +get_all(self, model_class, offset, limit, order_by, filters)
        ... +10 more methods
    }
    class DatabaseSchema {
        +__init__(self, connection)
        +create_all_tables(self)
        +check_table_exists(self, table_name)
        +get_table_list(self)
        +get_table_columns(self, table_name)
        ... +4 more methods
    }
    class MediaHandler {
        +__init__(self, base_media_path)
        +store_file(self, file_path, entity_type, entity_id, description, tags, author)
        +get_file_path(self, media_filename, entity_type, entity_id)
        +delete_file(self, media_filename, entity_type, entity_id)
        +get_media_info(self, file_path)
        ... +2 more methods
    }
    class HarrisMatrixGenerator {
        +__init__(self, db_manager)
        +generate_matrix(self, site_name, area)
        +get_matrix_levels(self, graph)
        +get_matrix_statistics(self, graph)
        +add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)
    }
    class MatrixVisualizer {
        +__init__(self)
        +render_matplotlib(self, graph, levels, output_path, style)
        +render_graphviz(self, graph, output_path)
        +create_interactive_html(self, graph, levels)
        +export_to_formats(self, graph, levels, base_filename)
    }
    class BaseValidator {
        +validate_required_fields(data, required_fields)
        +validate_string_length(value, field_name, max_length, min_length)
        +validate_numeric_range(value, field_name, min_value, max_value)
    }
    class SiteValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- SiteValidator
    class USValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- USValidator
    class InventarioValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- InventarioValidator
    class ThesaurusSigle {
        +__repr__(self)
        +display_value(self)
    }
    BaseModel <|-- ThesaurusSigle
    class ThesaurusField {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- ThesaurusField
    class ThesaurusCategory {
        +__repr__(self)
    }
    BaseModel <|-- ThesaurusCategory
    class Media {
        +__repr__(self)
        +is_image(self)
        +is_document(self)
    }
    BaseModel <|-- Media
    class MediaThumb {
        +__repr__(self)
    }
    BaseModel <|-- MediaThumb
    class Documentation {
        +__repr__(self)
    }
    BaseModel <|-- Documentation
    class PyArchInitMiniError {
    }
    Exception <|-- PyArchInitMiniError
    class DatabaseError {
    }
    PyArchInitMiniError <|-- DatabaseError
    class ValidationError {
        +__init__(self, message, field, value)
    }
    PyArchInitMiniError <|-- ValidationError
    class RecordNotFoundError {
    }
    PyArchInitMiniError <|-- RecordNotFoundError
    class DuplicateRecordError {
    }
    PyArchInitMiniError <|-- DuplicateRecordError
    class ConnectionError {
    }
    PyArchInitMiniError <|-- ConnectionError
    class ConfigurationError {
    }
    PyArchInitMiniError <|-- ConfigurationError
    class PermissionError {
    }
    PyArchInitMiniError <|-- PermissionError
    class US {
        +__repr__(self)
        +display_name(self)
        +full_identifier(self)
    }
    BaseModel <|-- US
    class Site {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- Site
    class HarrisMatrix {
        +__repr__(self)
    }
    BaseModel <|-- HarrisMatrix
    class USRelationships {
        +__repr__(self)
    }
    BaseModel <|-- USRelationships
    class Period {
        +__repr__(self)
    }
    BaseModel <|-- Period
    class Periodizzazione {
        +__repr__(self)
        +dating_range(self)
    }
    BaseModel <|-- Periodizzazione
    class BaseModel {
        +to_dict(self)
        +update_from_dict(self, data)
    }
    Base <|-- BaseModel
    class PDFGenerator {
        +__init__(self)
        +generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)
        +generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)
    }
    class InventarioMateriali {
        +__repr__(self)
        +display_name(self)
        +context_info(self)
    }
    BaseModel <|-- InventarioMateriali
    class BaseSchema {
    }
    BaseModel <|-- BaseSchema
    class SiteBase {
    }
    BaseModel <|-- SiteBase
    class SiteCreate {
    }
    SiteBase <|-- SiteCreate
    class SiteUpdate {
    }
    BaseModel <|-- SiteUpdate
    class SiteResponse {
    }
    SiteBase <|-- SiteResponse
    BaseSchema <|-- SiteResponse
    class USBase {
    }
    BaseModel <|-- USBase
    class USCreate {
    }
    USBase <|-- USCreate
    class USUpdate {
    }
    BaseModel <|-- USUpdate
    class USResponse {
    }
    USBase <|-- USResponse
    BaseSchema <|-- USResponse
    class InventarioBase {
        +validate_yes_no_fields(cls, v)
    }
    BaseModel <|-- InventarioBase
    class InventarioCreate {
    }
    InventarioBase <|-- InventarioCreate
    class InventarioUpdate {
    }
    BaseModel <|-- InventarioUpdate
    class InventarioResponse {
    }
    InventarioBase <|-- InventarioResponse
    BaseSchema <|-- InventarioResponse
    class PaginationParams {
    }
    BaseModel <|-- PaginationParams
    class PaginatedResponse {
    }
    BaseModel <|-- PaginatedResponse
    class Config {
    }
    class Config {
    }
    class ThesaurusService {
        +__init__(self, db_manager)
        +get_field_values(self, table_name, field_name, language)
        +add_field_value(self, table_name, field_name, value, label, description, language)
        +update_field_value(self, field_id, value, label, description)
        +delete_field_value(self, field_id)
        ... +3 more methods
    }
    class PeriodizzazioneService {
        +__init__(self, db_manager)
        +create_period(self, period_data)
        +get_period_by_id(self, period_id)
        +get_all_periods(self, page, size, filters)
        +search_periods(self, search_term, page, size)
        ... +15 more methods
    }
    class InventarioService {
        +__init__(self, db_manager)
        +create_inventario(self, inv_data)
        +get_inventario_by_id(self, inv_id)
        +get_inventario_dto_by_id(self, inv_id)
        +get_all_inventario(self, page, size, filters)
        ... +9 more methods
    }
    class MediaService {
        +__init__(self, db_manager, media_handler)
        +create_media_record(self, media_data)
        +store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)
        +get_media_by_id(self, media_id)
        +get_all_media(self, page, size, filters)
        ... +12 more methods
    }
    class DocumentationService {
        +__init__(self, db_manager)
        +create_documentation(self, doc_data)
        +get_documentation_by_id(self, doc_id)
        +get_documentation_by_entity(self, entity_type, entity_id, page, size)
        +get_all_documentation(self, page, size, filters)
        ... +3 more methods
    }
    class USService {
        +__init__(self, db_manager)
        +create_us(self, us_data)
        +get_us_by_id(self, us_id)
        +get_us_dto_by_id(self, us_id)
        +get_all_us(self, page, size, filters)
        ... +8 more methods
    }
    class SiteService {
        +__init__(self, db_manager)
        +create_site(self, site_data)
        +get_site_by_id(self, site_id)
        +get_site_dto_by_id(self, site_id)
        +get_site_by_name(self, site_name)
        ... +9 more methods
    }
    class ExtendedInventarioDialog {
        +__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)
        +center_window(self)
        +create_media_directory(self)
        +get_thesaurus_values(self, field_name)
        +create_identification_tab(self)
        ... +21 more methods
    }
    class PostgreSQLInstallerDialog {
        +__init__(self, parent, postgres_installer, callback)
        +center_window(self)
        +create_interface(self)
        +log_message(self, message)
        +update_progress(self, value, message)
        ... +6 more methods
    }
    class PyArchInitGUI {
        +__init__(self)
        +setup_database(self)
        +setup_styles(self)
        +create_menu(self)
        +create_main_interface(self)
        ... +44 more methods
    }
    class ThesaurusDialog {
        +__init__(self, parent, thesaurus_service, callback)
        +center_window(self)
        +create_interface(self)
        +create_details_form(self, parent)
        +load_tables(self)
        ... +12 more methods
    }
    class ExtendedUSDialog {
        +__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)
        +create_interface(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        +create_physical_tab(self)
        ... +31 more methods
    }
    class RelationshipDialog {
        +__init__(self, parent, us, matrix_generator, callback)
        +create_interface(self)
        +save_relationship(self)
        +cancel(self)
    }
    class PeriodizationDialog {
        +__init__(self, parent, us, periodizzazione_service, callback)
        +create_interface(self)
        +create_chronology_tab(self)
        +create_phases_tab(self)
        +create_dating_tab(self)
        ... +3 more methods
    }
    class ChronologicalSequenceDialog {
        +__init__(self, parent, site_name, us_service, periodizzazione_service)
        +create_interface(self)
        +create_timeline_tab(self)
        +create_periods_tab(self)
        +create_matrix_tab(self)
        ... +7 more methods
    }
    class BaseDialog {
        +__init__(self, parent, title, width, height)
        +center_window(self)
        +create_buttons(self, ok_text, cancel_text)
        +ok(self)
        +cancel(self)
    }
    class SiteDialog {
        +__init__(self, parent, site_service, media_service, site, callback)
        +create_media_directory(self)
        +create_form(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        ... +11 more methods
    }
    BaseDialog <|-- SiteDialog
    class USDialog {
        +__init__(self, parent, us_service, site_names, us, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- USDialog
    class InventarioDialog {
        +__init__(self, parent, inventario_service, site_names, inventario, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- InventarioDialog
    class HarrisMatrixDialog {
        +__init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)
        +create_interface(self)
        +generate_matrix(self)
        +display_statistics(self, stats)
        +display_levels(self)
        ... +2 more methods
    }
    BaseDialog <|-- HarrisMatrixDialog
    class PDFExportDialog {
        +__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)
        +create_interface(self)
        +select_output_file(self)
        +ok(self)
    }
    BaseDialog <|-- PDFExportDialog
    class DatabaseConfigDialog {
        +__init__(self, parent, callback)
        +create_interface(self)
        +on_db_type_change(self)
        +browse_sqlite_file(self)
        +test_connection(self)
        ... +2 more methods
    }
    BaseDialog <|-- DatabaseConfigDialog
    class MediaManagerDialog {
        +__init__(self, parent, media_handler)
        +create_interface(self)
        +select_file(self)
        +upload_file(self)
    }
    BaseDialog <|-- MediaManagerDialog
    class StatisticsDialog {
        +__init__(self, parent, site_service, us_service, inventario_service)
        +create_interface(self)
        +load_statistics(self)
    }
    BaseDialog <|-- StatisticsDialog
    class HarrisMatrixEditor {
        +__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)
        +create_interface(self)
        +create_control_panel(self, parent)
        +create_left_panel(self, parent)
        +create_relationships_tab(self, parent)
        ... +26 more methods
    }
    class PyArchInitCLI {
        +__init__(self, database_url)
        +show_welcome(self)
        +show_main_menu(self)
        +sites_menu(self)
        +list_sites(self)
        ... +9 more methods
    }
    class SampleDataGenerator {
        +__init__(self, db_manager)
        +create_site(self)
        +create_periods(self)
        +create_thesaurus(self)
        +create_us_records(self, site)
        ... +4 more methods
    }
    class SiteForm {
    }
    FlaskForm <|-- SiteForm
    class USForm {
    }
    FlaskForm <|-- USForm
    class InventarioForm {
    }
    FlaskForm <|-- InventarioForm
    class MediaUploadForm {
    }
    FlaskForm <|-- MediaUploadForm
    class InventarioDTO {
        +from_model(cls, inventario_model)
        +to_dict(self)
        +display_name(self)
    }
    class SiteDTO {
        +from_model(cls, site_model)
        +to_dict(self)
        +display_name(self)
    }
    class USDTO {
        +from_model(cls, us_model)
        +to_dict(self)
        +display_name(self)
    }
    class PyArchInitError {
    }
    Exception <|-- PyArchInitError
    class DatabaseError {
    }
    PyArchInitError <|-- DatabaseError
    class ValidationError {
    }
    PyArchInitError <|-- ValidationError
    class ServiceError {
    }
    PyArchInitError <|-- ServiceError
    class ConfigurationError {
    }
    PyArchInitError <|-- ConfigurationError
    class DatabaseSchema {
        +__init__(self, connection)
        +create_all_tables(self)
        +check_table_exists(self, table_name)
        +get_table_list(self)
        +get_table_columns(self, table_name)
        ... +4 more methods
    }
    class DatabaseConnection {
        +__init__(self, connection_string)
        +get_session(self)
        +create_tables(self)
        +initialize_database(self)
        +test_connection(self)
        ... +4 more methods
    }
    class DatabaseMigrations {
        +__init__(self, db_manager)
        +check_column_exists(self, table_name, column_name)
        +add_column_if_not_exists(self, table_name, column_name, column_type, default_value)
        +migrate_inventario_materiali_table(self)
        +migrate_all_tables(self)
        ... +2 more methods
    }
    class RecordNotFoundError {
    }
    DatabaseError <|-- RecordNotFoundError
    class DatabaseManager {
        +__init__(self, connection)
        +run_migrations(self)
        +create(self, model_class, data)
        +get_by_id(self, model_class, record_id)
        +get_by_field(self, model_class, field_name, value)
        ... +11 more methods
    }
    class PostgreSQLInstaller {
        +__init__(self)
        +check_postgres_installed(self)
        +get_postgres_version(self)
        +install_postgres_macos(self)
        +install_postgres_windows(self)
        ... +4 more methods
    }
    class MatrixVisualizer {
        +__init__(self)
        +render_matplotlib(self, graph, levels, output_path, style)
        +render_graphviz(self, graph, output_path)
        +create_interactive_html(self, graph, levels)
        +export_to_formats(self, graph, levels, base_filename)
    }
    class HarrisMatrixGenerator {
        +__init__(self, db_manager, us_service)
        +generate_matrix(self, site_name, area)
        +get_matrix_levels(self, graph)
        +get_matrix_statistics(self, graph)
        +add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)
    }
    class MediaHandler {
        +__init__(self, base_media_path)
        +store_file(self, file_path, entity_type, entity_id, description, tags, author)
        +get_file_path(self, media_filename, entity_type, entity_id)
        +delete_file(self, media_filename, entity_type, entity_id)
        +get_media_info(self, file_path)
        ... +2 more methods
    }
    class Media {
        +__repr__(self)
        +is_image(self)
        +is_document(self)
    }
    BaseModel <|-- Media
    class MediaThumb {
        +__repr__(self)
    }
    BaseModel <|-- MediaThumb
    class Documentation {
        +__repr__(self)
    }
    BaseModel <|-- Documentation
    class BaseValidator {
        +validate_required_fields(data, required_fields)
        +validate_string_length(value, field_name, max_length, min_length)
        +validate_numeric_range(value, field_name, min_value, max_value)
    }
    class SiteValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- SiteValidator
    class USValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- USValidator
    class InventarioValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- InventarioValidator
    class ThesaurusSigle {
        +__repr__(self)
        +display_value(self)
    }
    BaseModel <|-- ThesaurusSigle
    class ThesaurusField {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- ThesaurusField
    class ThesaurusCategory {
        +__repr__(self)
    }
    BaseModel <|-- ThesaurusCategory
    class PyArchInitMiniError {
    }
    Exception <|-- PyArchInitMiniError
    class DatabaseError {
    }
    PyArchInitMiniError <|-- DatabaseError
    class ValidationError {
        +__init__(self, message, field, value)
    }
    PyArchInitMiniError <|-- ValidationError
    class RecordNotFoundError {
    }
    PyArchInitMiniError <|-- RecordNotFoundError
    class DuplicateRecordError {
    }
    PyArchInitMiniError <|-- DuplicateRecordError
    class ConnectionError {
    }
    PyArchInitMiniError <|-- ConnectionError
    class ConfigurationError {
    }
    PyArchInitMiniError <|-- ConfigurationError
    class PermissionError {
    }
    PyArchInitMiniError <|-- PermissionError
    class InventarioMateriali {
        +__repr__(self)
        +display_name(self)
        +context_info(self)
    }
    BaseModel <|-- InventarioMateriali
    class Site {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- Site
    class US {
        +__repr__(self)
        +display_name(self)
        +full_identifier(self)
    }
    BaseModel <|-- US
    class HarrisMatrix {
        +__repr__(self)
    }
    BaseModel <|-- HarrisMatrix
    class USRelationships {
        +__repr__(self)
    }
    BaseModel <|-- USRelationships
    class Period {
        +__repr__(self)
    }
    BaseModel <|-- Period
    class Periodizzazione {
        +__repr__(self)
        +dating_range(self)
    }
    BaseModel <|-- Periodizzazione
    class BaseModel {
        +to_dict(self)
        +update_from_dict(self, data)
    }
    Base <|-- BaseModel
    class PDFGenerator {
        +__init__(self)
        +generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)
        +generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)
        +generate_us_pdf(self, site_name, us_list, output_path)
        +generate_inventario_pdf(self, site_name, inventario_list, output_path)
    }
    class BaseSchema {
    }
    BaseModel <|-- BaseSchema
    class SiteBase {
    }
    BaseModel <|-- SiteBase
    class SiteCreate {
    }
    SiteBase <|-- SiteCreate
    class SiteUpdate {
    }
    BaseModel <|-- SiteUpdate
    class SiteResponse {
    }
    SiteBase <|-- SiteResponse
    BaseSchema <|-- SiteResponse
    class USBase {
    }
    BaseModel <|-- USBase
    class USCreate {
    }
    USBase <|-- USCreate
    class USUpdate {
    }
    BaseModel <|-- USUpdate
    class USResponse {
    }
    USBase <|-- USResponse
    BaseSchema <|-- USResponse
    class InventarioBase {
        +validate_yes_no_fields(cls, v)
    }
    BaseModel <|-- InventarioBase
    class InventarioCreate {
    }
    InventarioBase <|-- InventarioCreate
    class InventarioUpdate {
    }
    BaseModel <|-- InventarioUpdate
    class InventarioResponse {
    }
    InventarioBase <|-- InventarioResponse
    BaseSchema <|-- InventarioResponse
    class PaginationParams {
    }
    BaseModel <|-- PaginationParams
    class PaginatedResponse {
    }
    BaseModel <|-- PaginatedResponse
    class Config {
    }
    class Config {
    }
    class PeriodizzazioneService {
        +__init__(self, db_manager)
        +create_period(self, period_data)
        +get_period_by_id(self, period_id)
        +get_all_periods(self, page, size, filters)
        +search_periods(self, search_term, page, size)
        ... +15 more methods
    }
    class ThesaurusService {
        +__init__(self, db_manager)
        +get_field_values(self, table_name, field_name, language)
        +add_field_value(self, table_name, field_name, value, label, description, language)
        +update_field_value(self, field_id, value, label, description)
        +delete_field_value(self, field_id)
        ... +3 more methods
    }
    class USService {
        +__init__(self, db_manager)
        +create_us(self, us_data)
        +create_us_dto(self, us_data)
        +get_us_by_id(self, us_id)
        +get_us_dto_by_id(self, us_id)
        ... +9 more methods
    }
    class MediaService {
        +__init__(self, db_manager, media_handler)
        +create_media_record(self, media_data)
        +store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)
        +get_media_by_id(self, media_id)
        +get_all_media(self, page, size, filters)
        ... +12 more methods
    }
    class DocumentationService {
        +__init__(self, db_manager)
        +create_documentation(self, doc_data)
        +get_documentation_by_id(self, doc_id)
        +get_documentation_by_entity(self, entity_type, entity_id, page, size)
        +get_all_documentation(self, page, size, filters)
        ... +3 more methods
    }
    class SiteService {
        +__init__(self, db_manager)
        +create_site(self, site_data)
        +create_site_dto(self, site_data)
        +get_site_by_id(self, site_id)
        +get_site_dto_by_id(self, site_id)
        ... +13 more methods
    }
    class InventarioService {
        +__init__(self, db_manager)
        +create_inventario(self, inv_data)
        +create_inventario_dto(self, inv_data)
        +get_inventario_by_id(self, inv_id)
        +get_inventario_dto_by_id(self, inv_id)
        ... +11 more methods
    }
    class PyArchInitGUI {
        +__init__(self)
        +setup_database(self)
        +setup_styles(self)
        +create_menu(self)
        +create_main_interface(self)
        ... +48 more methods
    }
    class PostgreSQLInstallerDialog {
        +__init__(self, parent, postgres_installer, callback)
        +center_window(self)
        +create_interface(self)
        +log_message(self, message)
        +update_progress(self, value, message)
        ... +6 more methods
    }
    class ExtendedInventarioDialog {
        +__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)
        +center_window(self)
        +create_media_directory(self)
        +get_thesaurus_values(self, field_name)
        +create_identification_tab(self)
        ... +21 more methods
    }
    class ExtendedUSDialog {
        +__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)
        +create_interface(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        +create_physical_tab(self)
        ... +31 more methods
    }
    class RelationshipDialog {
        +__init__(self, parent, us, matrix_generator, callback)
        +create_interface(self)
        +save_relationship(self)
        +cancel(self)
    }
    class PeriodizationDialog {
        +__init__(self, parent, us, periodizzazione_service, callback)
        +create_interface(self)
        +create_chronology_tab(self)
        +create_phases_tab(self)
        +create_dating_tab(self)
        ... +3 more methods
    }
    class ChronologicalSequenceDialog {
        +__init__(self, parent, site_name, us_service, periodizzazione_service)
        +create_interface(self)
        +create_timeline_tab(self)
        +create_periods_tab(self)
        +create_matrix_tab(self)
        ... +7 more methods
    }
    class HarrisMatrixEditor {
        +__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)
        +create_interface(self)
        +create_control_panel(self, parent)
        +create_left_panel(self, parent)
        +create_relationships_tab(self, parent)
        ... +26 more methods
    }
    class ThesaurusDialog {
        +__init__(self, parent, thesaurus_service, callback)
        +center_window(self)
        +create_interface(self)
        +create_details_form(self, parent)
        +load_tables(self)
        ... +12 more methods
    }
    class BaseDialog {
        +__init__(self, parent, title, width, height)
        +center_window(self)
        +create_buttons(self, ok_text, cancel_text)
        +ok(self)
        +cancel(self)
    }
    class SiteDialog {
        +__init__(self, parent, site_service, media_service, site, callback)
        +create_media_directory(self)
        +create_form(self)
        +create_basic_tab(self)
        +create_description_tab(self)
        ... +11 more methods
    }
    BaseDialog <|-- SiteDialog
    class USDialog {
        +__init__(self, parent, us_service, site_names, us, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- USDialog
    class InventarioDialog {
        +__init__(self, parent, inventario_service, site_names, inventario, callback)
        +create_form(self)
        +populate_form(self)
        +ok(self)
    }
    BaseDialog <|-- InventarioDialog
    class HarrisMatrixDialog {
        +__init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)
        +create_interface(self)
        +generate_matrix(self)
        +display_statistics(self, stats)
        +display_levels(self)
        ... +11 more methods
    }
    BaseDialog <|-- HarrisMatrixDialog
    class PDFExportDialog {
        +__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)
        +create_interface(self)
        +select_output_file(self)
        +ok(self)
    }
    BaseDialog <|-- PDFExportDialog
    class DatabaseConfigDialog {
        +__init__(self, parent, callback)
        +create_interface(self)
        +on_db_type_change(self)
        +browse_sqlite_file(self)
        +use_sample_database(self)
        ... +6 more methods
    }
    BaseDialog <|-- DatabaseConfigDialog
    class MediaManagerDialog {
        +__init__(self, parent, media_handler)
        +create_interface(self)
        +select_file(self)
        +upload_file(self)
    }
    BaseDialog <|-- MediaManagerDialog
    class StatisticsDialog {
        +__init__(self, parent, site_service, us_service, inventario_service)
        +create_interface(self)
        +load_statistics(self)
    }
    BaseDialog <|-- StatisticsDialog
    class SiteForm {
    }
    FlaskForm <|-- SiteForm
    class USForm {
    }
    FlaskForm <|-- USForm
    class InventarioForm {
    }
    FlaskForm <|-- InventarioForm
    class MediaUploadForm {
    }
    FlaskForm <|-- MediaUploadForm
    class PyArchInitCLI {
        +__init__(self, database_url)
        +show_welcome(self)
        +show_main_menu(self)
        +sites_menu(self)
        +list_sites(self)
        ... +9 more methods
    }
    class SampleDataGenerator {
        +__init__(self, db_manager)
        +create_site(self)
        +create_periods(self)
        +create_thesaurus(self)
        +create_us_records(self, site)
        ... +4 more methods
    }
    class USDTO {
        +from_model(cls, us_model)
        +to_dict(self)
        +display_name(self)
    }
    class InventarioDTO {
        +from_model(cls, inventario_model)
        +to_dict(self)
        +display_name(self)
    }
    class PyArchInitError {
    }
    Exception <|-- PyArchInitError
    class DatabaseError {
    }
    PyArchInitError <|-- DatabaseError
    class ValidationError {
    }
    PyArchInitError <|-- ValidationError
    class ServiceError {
    }
    PyArchInitError <|-- ServiceError
    class ConfigurationError {
    }
    PyArchInitError <|-- ConfigurationError
    class DatabaseConnection {
        +__init__(self, connection_string)
        +get_session(self)
        +create_tables(self)
        +initialize_database(self)
        +test_connection(self)
        ... +4 more methods
    }
    class SiteDTO {
        +from_model(cls, site_model)
        +to_dict(self)
        +display_name(self)
    }
    class PostgreSQLInstaller {
        +__init__(self)
        +check_postgres_installed(self)
        +get_postgres_version(self)
        +install_postgres_macos(self)
        +install_postgres_windows(self)
        ... +4 more methods
    }
    class DatabaseSchema {
        +__init__(self, connection)
        +create_all_tables(self)
        +check_table_exists(self, table_name)
        +get_table_list(self)
        +get_table_columns(self, table_name)
        ... +4 more methods
    }
    class DatabaseMigrations {
        +__init__(self, db_manager)
        +check_column_exists(self, table_name, column_name)
        +add_column_if_not_exists(self, table_name, column_name, column_type, default_value)
        +migrate_inventario_materiali_table(self)
        +migrate_all_tables(self)
        ... +2 more methods
    }
    class RecordNotFoundError {
    }
    DatabaseError <|-- RecordNotFoundError
    class DatabaseManager {
        +__init__(self, connection)
        +run_migrations(self)
        +create(self, model_class, data)
        +get_by_id(self, model_class, record_id)
        +get_by_field(self, model_class, field_name, value)
        ... +11 more methods
    }
    class MediaHandler {
        +__init__(self, base_media_path)
        +store_file(self, file_path, entity_type, entity_id, description, tags, author)
        +get_file_path(self, media_filename, entity_type, entity_id)
        +delete_file(self, media_filename, entity_type, entity_id)
        +get_media_info(self, file_path)
        ... +2 more methods
    }
    class PyArchInitMatrixVisualizer {
        +__init__(self)
        +create_matrix(self, graph, grouping, settings, output_path)
        +export_multiple_formats(self, graph, base_filename, grouping)
    }
    class EnhancedHarrisMatrixVisualizer {
        +__init__(self)
        +create_graphviz_matrix(self, graph, grouping, output_format, output_path)
        +create_temporal_matrix(self, graph, output_path)
        +export_multiple_formats(self, graph, base_filename, grouping)
        +create_relationship_legend(self, output_path)
        ... +1 more methods
    }
    class MatrixVisualizer {
        +__init__(self)
        +render_matplotlib(self, graph, levels, output_path, style)
        +render_graphviz(self, graph, output_path)
        +create_interactive_html(self, graph, levels)
        +export_to_formats(self, graph, levels, base_filename)
    }
    class HarrisMatrixGenerator {
        +__init__(self, db_manager, us_service)
        +generate_matrix(self, site_name, area)
        +get_matrix_levels(self, graph)
        +get_matrix_statistics(self, graph)
        +add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)
    }
    class Media {
        +__repr__(self)
        +is_image(self)
        +is_document(self)
    }
    BaseModel <|-- Media
    class MediaThumb {
        +__repr__(self)
    }
    BaseModel <|-- MediaThumb
    class Documentation {
        +__repr__(self)
    }
    BaseModel <|-- Documentation
    class BaseValidator {
        +validate_required_fields(data, required_fields)
        +validate_string_length(value, field_name, max_length, min_length)
        +validate_numeric_range(value, field_name, min_value, max_value)
    }
    class SiteValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- SiteValidator
    class USValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- USValidator
    class InventarioValidator {
        +validate(cls, data)
    }
    BaseValidator <|-- InventarioValidator
    class PyArchInitMiniError {
    }
    Exception <|-- PyArchInitMiniError
    class DatabaseError {
    }
    PyArchInitMiniError <|-- DatabaseError
    class ValidationError {
        +__init__(self, message, field, value)
    }
    PyArchInitMiniError <|-- ValidationError
    class RecordNotFoundError {
    }
    PyArchInitMiniError <|-- RecordNotFoundError
    class DuplicateRecordError {
    }
    PyArchInitMiniError <|-- DuplicateRecordError
    class ConnectionError {
    }
    PyArchInitMiniError <|-- ConnectionError
    class ConfigurationError {
    }
    PyArchInitMiniError <|-- ConfigurationError
    class PermissionError {
    }
    PyArchInitMiniError <|-- PermissionError
    class US {
        +__repr__(self)
        +display_name(self)
        +full_identifier(self)
    }
    BaseModel <|-- US
    class ThesaurusSigle {
        +__repr__(self)
        +display_value(self)
    }
    BaseModel <|-- ThesaurusSigle
    class ThesaurusField {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- ThesaurusField
    class ThesaurusCategory {
        +__repr__(self)
    }
    BaseModel <|-- ThesaurusCategory
    class Site {
        +__repr__(self)
        +display_name(self)
    }
    BaseModel <|-- Site
    class BaseModel {
        +to_dict(self)
        +update_from_dict(self, data)
    }
    Base <|-- BaseModel
    class InventarioMateriali {
        +__repr__(self)
        +display_name(self)
        +context_info(self)
    }
    BaseModel <|-- InventarioMateriali
    class HarrisMatrix {
        +__repr__(self)
    }
    BaseModel <|-- HarrisMatrix
    class USRelationships {
        +__repr__(self)
    }
    BaseModel <|-- USRelationships
    class Period {
        +__repr__(self)
    }
    BaseModel <|-- Period
    class Periodizzazione {
        +__repr__(self)
        +dating_range(self)
    }
    BaseModel <|-- Periodizzazione
    class PyArchInitInventoryTemplate {
        +__init__(self)
        +setup_styles(self)
        +generate_inventory_sheets(self, inventario_list, output_path, site_name)
        +generate_inventory_catalog(self, inventario_list, output_path, site_name)
    }
    class PDFGenerator {
        +__init__(self)
        +generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)
        +generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)
        +generate_us_pdf(self, site_name, us_list, output_path)
        +generate_inventario_pdf(self, site_name, inventario_list, output_path)
    }
    class BaseSchema {
    }
    BaseModel <|-- BaseSchema
    class SiteBase {
    }
    BaseModel <|-- SiteBase
    class SiteCreate {
    }
    SiteBase <|-- SiteCreate
    class SiteUpdate {
    }
    BaseModel <|-- SiteUpdate
    class SiteResponse {
    }
    SiteBase <|-- SiteResponse
    BaseSchema <|-- SiteResponse
    class USBase {
    }
    BaseModel <|-- USBase
    class USCreate {
    }
    USBase <|-- USCreate
    class USUpdate {
    }
    BaseModel <|-- USUpdate
    class USResponse {
    }
    USBase <|-- USResponse
    BaseSchema <|-- USResponse
    class InventarioBase {
        +validate_yes_no_fields(cls, v)
    }
    BaseModel <|-- InventarioBase
    class InventarioCreate {
    }
    InventarioBase <|-- InventarioCreate
    class InventarioUpdate {
    }
    BaseModel <|-- InventarioUpdate
    class InventarioResponse {
    }
    InventarioBase <|-- InventarioResponse
    BaseSchema <|-- InventarioResponse
    class PaginationParams {
    }
    BaseModel <|-- PaginationParams
    class PaginatedResponse {
    }
    BaseModel <|-- PaginatedResponse
    class Config {
    }
    class Config {
    }
    class PeriodizzazioneService {
        +__init__(self, db_manager)
        +create_period(self, period_data)
        +get_period_by_id(self, period_id)
        +get_all_periods(self, page, size, filters)
        +search_periods(self, search_term, page, size)
        ... +15 more methods
    }
    class ThesaurusService {
        +__init__(self, db_manager)
        +get_field_values(self, table_name, field_name, language)
        +add_field_value(self, table_name, field_name, value, label, description, language)
        +update_field_value(self, field_id, value, label, description)
        +delete_field_value(self, field_id)
        ... +3 more methods
    }
    class InventarioService {
        +__init__(self, db_manager)
        +create_inventario(self, inv_data)
        +create_inventario_dto(self, inv_data)
        +get_inventario_by_id(self, inv_id)
        +get_inventario_dto_by_id(self, inv_id)
        ... +11 more methods
    }
    class USService {
        +__init__(self, db_manager)
        +create_us(self, us_data)
        +create_us_dto(self, us_data)
        +get_us_by_id(self, us_id)
        +get_us_dto_by_id(self, us_id)
        ... +9 more methods
    }
    class MediaService {
        +__init__(self, db_manager, media_handler)
        +create_media_record(self, media_data)
        +store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)
        +get_media_by_id(self, media_id)
        +get_all_media(self, page, size, filters)
        ... +12 more methods
    }
    class DocumentationService {
        +__init__(self, db_manager)
        +create_documentation(self, doc_data)
        +get_documentation_by_id(self, doc_id)
        +get_documentation_by_entity(self, entity_type, entity_id, page, size)
        +get_all_documentation(self, page, size, filters)
        ... +3 more methods
    }
    class SiteService {
        +__init__(self, db_manager)
        +create_site(self, site_data)
        +create_site_dto(self, site_data)
        +get_site_by_id(self, site_id)
        +get_site_dto_by_id(self, site_id)
        ... +13 more methods
    }
```
