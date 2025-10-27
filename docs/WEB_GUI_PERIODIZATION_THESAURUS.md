# Web GUI: Periodization and Thesaurus Interfaces

## Version 1.5.8 - New Features

This document describes the newly implemented web interfaces for managing Periodization (Datazioni) and Thesaurus ICCD vocabularies in PyArchInit-Mini.

## Overview

Two new web interfaces have been added to the PyArchInit-Mini web GUI:

1. **Periodizzazione (Datazioni)** - Manage archaeological chronological datings
2. **Thesaurus ICCD** - Manage controlled vocabularies for ICCD standards

Both interfaces are accessible from the main navigation menu under the new **Configuration** section.

## Implementation Details

### Files Created

#### Routes (web_interface/app.py)
- Lines 2478-2676: Added 199 lines of new routes for both interfaces
- **Periodizzazione Routes** (lines 2478-2561):
  - `GET /periodizzazione` - List all datazioni
  - `GET/POST /periodizzazione/create` - Create new datazione
  - `GET/POST /periodizzazione/<id>/edit` - Edit existing datazione
  - `POST /periodizzazione/<id>/delete` - Delete datazione

- **Thesaurus Routes** (lines 2563-2676):
  - `GET /thesaurus` - List thesaurus with table/field selection
  - `POST /thesaurus/create` - Create new thesaurus value
  - `POST /thesaurus/<id>/edit` - Edit thesaurus value
  - `POST /thesaurus/<id>/delete` - Delete thesaurus value

#### Templates Created
- `web_interface/templates/periodizzazione/list.html` - List all datazioni
- `web_interface/templates/periodizzazione/form.html` - Create/edit datazione form
- `web_interface/templates/thesaurus/list.html` - Thesaurus management interface

#### Navigation Updated
- `web_interface/templates/base.html`:
  - Lines 390-398: Added "Configuration" dropdown menu
  - Lines 510-524: Added "Configuration" sidebar section

## Testing Instructions

### Starting the Web Server

From the project root directory:

```bash
cd web_interface
python app.py
```

The server will start on `http://localhost:5001/`

### Testing Periodizzazione Interface

1. **Navigate to Periodizzazione**
   - Click on **"Configuration"** in the main menu
   - Select **"Periodization"**
   - URL: `http://localhost:5001/periodizzazione`

2. **Create a New Datazione**
   - Click the **"Nuova Datazione"** button
   - Fill in the form:
     - **Nome Datazione** (required): e.g., "Età del Bronzo Antico"
     - **Fascia Cronologica** (optional): e.g., "2200-1700 a.C."
     - **Descrizione** (optional): Additional details
   - Click **"Salva"** to save
   - Verify success message appears
   - Verify new datazione appears in the list

3. **Edit an Existing Datazione**
   - In the list, click the **"Modifica"** button for any datazione
   - Update the fields
   - Click **"Salva"**
   - Verify the changes appear in the list

4. **Delete a Datazione**
   - In the list, click the **"Elimina"** button for any datazione
   - Confirm the deletion in the popup dialog
   - Verify the datazione is removed from the list

### Testing Thesaurus Interface

1. **Navigate to Thesaurus**
   - Click on **"Configuration"** in the main menu
   - Select **"Thesaurus ICCD"**
   - URL: `http://localhost:5001/thesaurus`

2. **Select Table and Field**
   - In the first dropdown, select a table (e.g., "us_table")
   - The page will refresh and show available fields
   - In the second dropdown, select a field (e.g., "stato_conservazione")
   - The page will refresh and show existing values for that field

3. **Add a New Thesaurus Value**
   - In the "Aggiungi Nuovo Valore" form:
     - **Valore** (required): The vocabulary value (e.g., "Ottimo")
     - **Etichetta** (optional): A readable label
     - **Descrizione** (optional): Description of the value
   - Click **"Aggiungi"**
   - Verify success message
   - Verify the new value appears in the table

4. **Edit a Thesaurus Value (Inline Editing)**
   - In the values table, click the **pencil icon** (Modifica) for any row
   - The row will switch to edit mode with input fields
   - Modify the value, label, or description
   - Click the **checkmark icon** (Salva) to save
   - Or click the **X icon** (Annulla) to cancel
   - Verify the updated value appears in the table

5. **Delete a Thesaurus Value**
   - In the values table, click the **trash icon** (Elimina) for any row
   - Confirm the deletion in the popup dialog
   - Verify the value is removed from the table

### Test Cases Checklist

#### Periodizzazione
- [ ] View empty list message when no datazioni exist
- [ ] Create new datazione with all fields
- [ ] Create new datazione with only required field (nome_datazione)
- [ ] Edit existing datazione
- [ ] Delete datazione with confirmation
- [ ] Verify total count updates correctly
- [ ] Check that long descriptions are truncated in the list view

#### Thesaurus
- [ ] Select different tables from dropdown
- [ ] Select different fields for each table
- [ ] View empty message when no values exist for a field
- [ ] Create new thesaurus value with all fields
- [ ] Create new thesaurus value with only required field (value)
- [ ] Edit thesaurus value using inline editing
- [ ] Cancel inline editing without saving
- [ ] Delete thesaurus value with confirmation
- [ ] Verify badge count updates correctly

### Navigation Testing
- [ ] Verify "Configuration" appears in main dropdown menu
- [ ] Verify "Configuration" appears in sidebar
- [ ] Verify both links work from dropdown menu
- [ ] Verify both links work from sidebar
- [ ] Verify breadcrumbs/navigation consistency

## Integration with Existing Features

### Periodizzazione
- The datazioni created here are used in the US forms
- The `campo_datazione` dropdown in US forms will show these values
- Integration point: `web_interface/app.py` US form routes

### Thesaurus
- The thesaurus values manage controlled vocabularies for all ICCD fields
- Values defined here appear in dropdowns throughout the application
- Tables supported include:
  - `us_table` - Unità Stratigrafiche
  - `inventario_materiali_table` - Material Inventory
  - `sito_table` - Sites
  - Others as defined in `THESAURUS_MAPPINGS`

## Error Handling

Both interfaces include comprehensive error handling:
- Database errors are caught and displayed as flash messages
- Missing records return appropriate error messages
- Form validation prevents empty required fields
- Delete confirmations prevent accidental deletions
- Graceful degradation if services are unavailable

## Security

- All routes protected with `@login_required` decorator
- Write operations protected with `@write_permission_required` decorator
- Delete operations require confirmation dialogs
- CSRF protection via Flask forms

## Known Issues / Future Improvements

- [ ] Add pagination for large lists
- [ ] Add search/filter functionality
- [ ] Add bulk operations (delete multiple, import/export)
- [ ] Add sorting options for table columns
- [ ] Add validation for duplicate values in thesaurus
- [ ] Add Italian translations for UI strings

## Version Information

- **Version**: 1.5.8
- **Date**: October 27, 2025
- **Feature**: Web GUI for Periodization and Thesaurus ICCD
- **Status**: Ready for testing
