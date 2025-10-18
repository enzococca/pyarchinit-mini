# web_interface/app.py

## Overview

This file contains 54 documented elements.

## Classes

### SiteForm

The `SiteForm` class is a Flask-WTF form used to collect and validate information about archaeological sites within a web application. It includes fields for site name, country, region, municipality, province, site definition, and a description, ensuring required data such as the site name is provided. This form facilitates standardized data entry for site records in the application.

**Inherits from**: FlaskForm

### USForm

The **USForm** class defines a structured web form for recording and managing archaeological stratigraphic units ("Unità Stratigrafiche") using Flask-WTF. It collects detailed information such as site, area, stratigraphic and interpretive descriptions, inventory numbers, excavation year, and formation type. This form ensures standardized data entry for stratigraphic records in archaeological projects.

**Inherits from**: FlaskForm

### InventarioForm

The `InventarioForm` class defines a structured web form for recording and managing inventory data of archaeological artifacts within a Flask application. It captures essential details such as site, inventory number, artifact type, definition, description, area, stratigraphic unit (US), and weight. The form ensures data integrity through field validations and standardized input choices for consistent cataloging.

**Inherits from**: FlaskForm

### MediaUploadForm

The `MediaUploadForm` class is a Flask-WTF form designed for uploading media files and associating them with specific entities within an application, such as a site, US, or inventory item. It collects essential metadata including the entity type and ID, the media file itself, an optional description, and author or photographer information. This form ensures all required fields are validated before processing uploads.

**Inherits from**: FlaskForm

### SiteForm

The **SiteForm** class is a Flask-WTF form used to collect and validate information about archaeological sites. It includes fields for site name, country, region, municipality, province, site definition, and a description. This form ensures that required data, such as the site name, is provided by the user before submission.

**Inherits from**: FlaskForm

### USForm

The `USForm` class is a Flask-WTF form designed for recording and managing archaeological stratigraphic unit (US) data within a web application. It collects detailed information such as site, area, stratigraphic and interpretative descriptions, excavation year, and other relevant metadata, ensuring comprehensive documentation of each stratigraphic unit. The form employs validation to ensure required fields are properly completed for accurate data entry.

**Inherits from**: FlaskForm

### InventarioForm

The `InventarioForm` class defines a web form for managing archaeological inventory records using Flask-WTF. It allows users to input and validate key artifact information such as site, inventory number, artifact type, definition, description, area, stratigraphic unit (US), and weight. This form ensures structured data entry for cataloging artifacts in an archaeological database.

**Inherits from**: FlaskForm

### MediaUploadForm

The `MediaUploadForm` class is a Flask-WTF form designed to facilitate the upload of media files associated with specific entities, such as sites, US (stratigraphic units), or inventory items. It allows users to specify the entity type and ID, upload a file, and optionally provide a description and author information. This form ensures that all required fields are validated before accepting the upload.

**Inherits from**: FlaskForm

### SiteForm

The `SiteForm` class is a Flask-WTF form designed for collecting and validating archaeological site information. It includes fields for site name, country, region, municipality, province, site definition, and a descriptive text, ensuring essential data is captured for each site entry. The form utilizes standard field types and validators to facilitate structured and accurate input.

**Inherits from**: FlaskForm

### USForm

The **USForm** class is a Flask-WTF form designed for the input and management of archaeological stratigraphic unit (US) data within a web application. It facilitates the collection of detailed information such as site, area, US number, stratigraphic and interpretative descriptions, excavation year, and formation type. This form ensures data integrity by enforcing required fields and standardized choices for key attributes.

**Inherits from**: FlaskForm

### InventarioForm

The `InventarioForm` class defines a Flask-WTF form for recording and managing archaeological inventory data. It includes fields for selecting a site, entering inventory numbers, specifying artifact type, providing definitions and descriptions, and recording contextual details such as area, stratigraphic unit (US), and weight. This form ensures structured data input for cataloging archaeological finds within a web application.

**Inherits from**: FlaskForm

### MediaUploadForm

The `MediaUploadForm` class defines a Flask-WTF form used for uploading media files associated with different entities (such as sites, US, or inventory items) within a web application. It collects essential metadata about the upload, including the entity type and ID, the file itself, an optional description, and the author's name. This form ensures that all required information is provided and properly validated before processing the upload.

**Inherits from**: FlaskForm

## Functions

### create_app()

The `create_app` function initializes and configures a Flask web application for managing archaeological site data, stratigraphic units (US), inventories, Harris matrices, and media uploads. It sets up the application configuration, database connections, service layers, and all primary routes for site management, data visualization, PDF export, and media handling. This function returns the fully configured Flask app instance, ready to be run as a web server.

### index()

Dashboard with statistics

### sites_list()

The `sites_list` function handles HTTP GET requests to the `/sites` route, displaying a paginated list of sites. It supports optional search functionality via a query parameter and renders the `sites/list.html` template with the retrieved sites, total count, current page, and search term.

### create_site()

The `create_site` function handles the creation of a new site record via a web form in a Flask application. It processes both GET and POST requests: displaying the empty form on GET, and validating and saving the form data on POST. Upon successful creation, it flashes a success message and redirects to the sites list; otherwise, it renders the form with error messages as needed.

### view_site(site_id)

The **`view_site`** function handles requests to display detailed information about a specific site identified by its `site_id`. It retrieves the site's data along with related US records and inventory items, and renders them in the `sites/detail.html` template. If the site is not found, it flashes an error message and redirects the user to the site list page.

**Parameters:**
- `site_id`

### us_list()

The `us_list` function is a Flask route handler that displays a paginated list of US records, optionally filtered by a site parameter provided via query string. It retrieves the filtered data and total count from the `us_service`, fetches available sites for filtering from `site_service`, and renders them in the `us/list.html` template along with pagination and filter information.

### create_us()

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form in a Flask application. It displays the form for input, populates site choices, validates submitted data, and, upon successful validation, creates the new record using the provided service. If creation is successful, it redirects to the US list page with a success message; otherwise, it displays appropriate error messages.

### inventario_list()

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, allowing optional filtering by site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and available site options, then renders the `inventario/list.html` template with the filtered results and pagination details.

### create_inventario()

The `create_inventario` function handles the creation of a new inventory record ("reperto") via a web form in a Flask application. It displays the form to the user, populates site choices, validates submitted data, and, upon successful validation, creates the inventory record using the provided service. If the creation is successful, it flashes a success message and redirects to the inventory list; otherwise, it displays an error message.

### harris_matrix(site_name)

The `harris_matrix` function is a Flask route handler that generates and displays the Harris Matrix for a given archaeological site, identified by `site_name`. It creates the matrix graph, calculates its levels and statistics, and renders a visualization, all of which are presented in the 'harris_matrix/view.html' template. If an error occurs during this process, the function flashes an error message and redirects the user to the site list page.

**Parameters:**
- `site_name`

### export_site_pdf(site_id)

The `export_site_pdf` function generates and downloads a PDF report containing detailed information about a specific site, including its associated US (stratigraphic units) and inventory records. When accessed via the `/export/site_pdf/<site_id>` route, it retrieves the site's data, compiles it into a PDF using a PDF generator, and returns the PDF file as a download to the user. If the site is not found or an error occurs during the process, the user is redirected with an appropriate error message.

**Parameters:**
- `site_id`

### upload_media()

The `upload_media` function handles both the display and processing of a media upload form. It allows users to upload a media file associated with a specific entity, temporarily saves and processes the file, stores its metadata using a media handler, and provides user feedback on the upload status. On successful upload, it also manages cleanup of the temporary file and redirects the user back to the upload page.

### api_sites()

The `api_sites` function is a Flask route handler that serves as an API endpoint at `/api/sites`. It retrieves up to 100 site records using the `site_service.get_all_sites` method and returns a JSON-formatted list of sites, where each site is represented by its `id` and `name` attributes. This endpoint is typically used for AJAX requests to dynamically fetch site information.

### create_app()

**Description:**

The `create_app` function initializes and configures a Flask web application for managing archaeological site data. It sets up application configuration, database connections, and service objects, and defines routes for CRUD operations on sites, stratigraphic units (US), inventory, Harris matrix generation, PDF export, media uploads, and API endpoints. This function serves as the main entry point for building and running the application.

### index()

Dashboard with statistics

### sites_list()

The `sites_list` function handles requests to the `/sites` route, displaying a paginated list of sites. It supports optional search functionality, retrieves the relevant sites from the database, and renders the `sites/list.html` template with the sites, pagination details, and search query.

### create_site()

The `create_site` function handles the creation of a new site record within the web application. It displays a form for user input, validates and processes the form submission, creates the site using the provided data, and provides user feedback on success or failure. Upon successful creation, it redirects to the site listing page; otherwise, it re-renders the form with error messages if needed.

### view_site(site_id)

The `view_site` function handles the display of detailed information for a specific site identified by its `site_id`. It retrieves the site's data along with related US and inventory records; if the site is not found, the user is redirected with an error message. Upon successful retrieval, it renders the detail page with all relevant information displayed.

**Parameters:**
- `site_id`

### us_list()

The `us_list` function handles the `/us` route and displays a paginated list of "us" records, optionally filtered by site (`sito`). It retrieves the current page number and filter parameters from the request, fetches the filtered list and total count from the service layer, and renders the results along with available sites in the `us/list.html` template.

### create_us()

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form. It displays the form to the user, populates site choices dynamically, validates the submitted data, and, upon successful validation, saves the new record using the `us_service`. If creation is successful, it flashes a success message and redirects to the US list; otherwise, it displays any errors encountered.

### inventario_list()

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, with optional filtering by site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and available site options, then renders the `inventario/list.html` template with the resulting list, filters, and pagination information.

### create_inventario()

The `create_inventario` function handles the creation of a new inventory record ("reperto") via a web form in a Flask application. It displays a form for entering inventory details, populates site choices dynamically, validates submitted data, and, upon successful submission, saves the new record using the inventory service. If creation is successful, it flashes a success message and redirects to the inventory list; otherwise, it handles errors and redisplays the form.

### harris_matrix(site_name)

The `harris_matrix` function is a Flask route that generates and displays the Harris Matrix for a given archaeological site, identified by `site_name`. It constructs the matrix graph, calculates its levels and statistical data, creates a visual representation, and renders these results in a dedicated template. If an error occurs during processing, it displays an error message and redirects the user to the sites list.

**Parameters:**
- `site_name`

### export_site_pdf(site_id)

The `export_site_pdf` function handles the export of a PDF report for a specific site, identified by its `site_id`. It retrieves the site's details and related data, generates a comprehensive PDF report, and sends the PDF as a downloadable file to the user. If the site is not found or an error occurs during export, the user is redirected with an appropriate error message.

**Parameters:**
- `site_id`

### upload_media()

The `upload_media` function handles the uploading of media files through a web form. It processes both GET and POST requests, validates the submitted form, saves the uploaded file temporarily, and delegates storage to a media handler with associated metadata. Upon successful upload, it provides user feedback and redirects, while handling errors gracefully and rendering the upload form as needed.

### api_sites()

The `api_sites` function is a Flask route handler that provides an API endpoint at `/api/sites`. When accessed, it retrieves up to 100 site records using the `site_service.get_all_sites` method and returns a JSON array containing the ID and name of each site. This endpoint is typically used for AJAX requests to populate site data dynamically in client-side applications.

### create_app()

The **`create_app`** function initializes and configures a Flask web application for managing archaeological site data, including sites, stratigraphic units (US), inventories, Harris matrices, and media uploads. It sets up essential configuration, database connections, service layers, and registers all routes for CRUD operations, data visualization, PDF export, and API endpoints. This function returns a fully configured Flask app instance ready to be run.

### index()

Dashboard with statistics

### sites_list()

The `sites_list` function handles the `/sites` route and displays a paginated list of sites, optionally filtered by a search query provided via the request parameters. It retrieves the relevant site data and the total count of sites from the `site_service`, then renders the 'sites/list.html' template with this information along with the current page and search term.

### create_site()

The `create_site` function handles the creation of a new site record via a web form within a Flask application. It displays the site creation form to the user, validates the submitted data, and, upon successful validation, saves the new site using the `site_service`. On success or failure, it provides user feedback and redirects appropriately.

### view_site(site_id)

The `view_site` function handles requests to display the details of a specific site identified by `site_id`. It retrieves the site's information, along with related US and inventory records, and renders them in the `sites/detail.html` template. If the site does not exist, the user is notified and redirected to the list of sites.

**Parameters:**
- `site_id`

### us_list()

The `us_list` function handles the `/us` route and displays a paginated list of "US" entries, with optional filtering by site ("sito"). It retrieves the relevant data from the service layer, gathers site options for filtering, and renders the `us/list.html` template with the results and filter parameters.

### create_us()

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form in a Flask application. It displays the form to the user, populates the site selection options, processes form submissions, and saves the new record to the database if validation succeeds, providing user feedback through flash messages. Upon successful creation, it redirects the user to the list of US records.

### inventario_list()

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, with optional filters for site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and site options, then renders the `inventario/list.html` template with the filtered results and pagination details. This view facilitates browsing and filtering of inventory records within the application.

### create_inventario()

The `create_inventario` function handles the creation of new inventory records (reperti) through a web form in a Flask application. It displays the form, populates site choices dynamically, validates user input, and upon successful submission, saves the new item to the database and provides user feedback. If any error occurs during the process, it flashes an error message and re-displays the form.

### harris_matrix(site_name)

The **harris_matrix** function is a Flask route that generates and displays the Harris Matrix for a given archaeological site, identified by its site name. It constructs the matrix graph, computes relevant levels and statistics, creates a visualization, and then renders these details in the 'harris_matrix/view.html' template. If an error occurs during processing, it flashes an error message and redirects the user to the site list page.

**Parameters:**
- `site_name`

### export_site_pdf(site_id)

The `export_site_pdf` function generates and exports a PDF report for a specific site, identified by its `site_id`. It retrieves the site's data along with related records, generates a comprehensive PDF report, and sends the file to the user as a downloadable attachment. If an error occurs or the site is not found, the function displays an appropriate error message and redirects the user accordingly.

**Parameters:**
- `site_id`

### upload_media()

The `upload_media` function handles the uploading of media files via a web form. It processes both GET and POST requests: displaying the upload form, validating submitted data, securely saving the uploaded file temporarily, and delegating the file storage to a media handler along with associated metadata. Upon successful upload or error, it provides user feedback and redirects appropriately.

### api_sites()

The `api_sites` function is a Flask route that provides an API endpoint at `/api/sites`. When accessed, it retrieves up to 100 site records using the `site_service`, and returns a JSON array containing the `id` and `name` of each site. This endpoint is typically used for AJAX requests to fetch site information dynamically.

