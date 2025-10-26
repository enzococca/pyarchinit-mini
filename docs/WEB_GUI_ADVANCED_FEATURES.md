# Web GUI Advanced Features Implementation Guide

## Overview

This document describes the implementation of advanced search, record navigation, and filtered exports for the PyArchInit-Mini web interface.

## Status

### ✅ Completed Features

1. **Advanced Search System for US**
   - Multi-field filtering (site, area, unit type, year, US number)
   - Filter persistence in session
   - Results counter
   - Responsive UI with Bootstrap cards

### 🔄 In Progress / To Complete

2. **Record Navigation in Detail View**
3. **Filtered PDF Export**
4. **Filtered Harris Matrix Export**
5. **Advanced Search for Inventory**

## Implemented Features

### 1. Advanced Search System (US)

**File**: `web_interface/app.py` - route `us_list()` (lines 644-717)

**Features**:
- Filters: site, area, unit_type, year, us_number
- Session storage for navigation consistency
- Dynamic dropdown population from database
- Results count display

**Template**: `web_interface/templates/us/list.html`

**Features**:
- Responsive filter card with Bootstrap
- Multiple filter fields in organized layout
- Results counter
- Reset button

**Usage**:
```python
# Filters are saved in session for use in navigation and exports
session['us_filters'] = {
    'sito': sito_filter,
    'area': area_filter,
    'unita_tipo': unita_tipo_filter,
    'anno_scavo': anno_scavo_filter,
    'periodo': periodo_filter,
    'fase': fase_filter,
    'us_number': us_number_filter
}
```

## To Implement

### 2. Record Navigation in Detail View (Prev/Next)

#### Implementation Plan

**Modify `edit_us()` route in `web_interface/app.py`**:

```python
@app.route('/us/<int:us_id>/edit', methods=['GET', 'POST'])
@login_required
@write_permission_required
def edit_us(us_id):
    from flask import session

    # Get filters from session
    filters = session.get('us_filters', {})

    # Build filters for query
    query_filters = {}
    if filters.get('sito'):
        query_filters['sito'] = filters['sito']
    if filters.get('area'):
        query_filters['area'] = filters['area']
    if filters.get('unita_tipo'):
        query_filters['unita_tipo'] = filters['unita_tipo']
    if filters.get('anno_scavo'):
        query_filters['anno_scavo'] = int(filters['anno_scavo'])
    if filters.get('us_number'):
        query_filters['us'] = filters['us_number']

    # Get full list of filtered US IDs
    all_us = us_service.get_all_us(size=10000, filters=query_filters)
    us_ids = [us.id_us for us in all_us]

    # Find current position
    try:
        current_index = us_ids.index(us_id)
    except ValueError:
        current_index = -1

    # Calculate prev/next
    prev_id = us_ids[current_index - 1] if current_index > 0 else None
    next_id = us_ids[current_index + 1] if current_index < len(us_ids) - 1 else None

    # Get existing US
    us = us_service.get_us_dto_by_id(us_id)
    if not us:
        flash('US non trovata', 'error')
        return redirect(url_for('us_list'))

    # ... rest of the function (form handling, etc.) ...

    # Pass navigation info to template
    return render_template('us/form.html',
                         form=form,
                         title='Modifica US',
                         edit_mode=True,
                         prev_id=prev_id,
                         next_id=next_id,
                         current_position=current_index + 1,
                         total_records=len(us_ids))
```

**Modify `web_interface/templates/us/form.html`**:

Add navigation bar after the title:

```html
{% if edit_mode and (prev_id or next_id) %}
<div class="alert alert-info mb-3">
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <i class="fas fa-info-circle"></i>
            Record <strong>{{ current_position }}</strong> of <strong>{{ total_records }}</strong>
        </div>
        <div class="btn-group" role="group">
            {% if prev_id %}
            <a href="{{ url_for('edit_us', us_id=prev_id) }}" class="btn btn-sm btn-outline-primary">
                <i class="fas fa-chevron-left"></i> Previous
            </a>
            {% else %}
            <button class="btn btn-sm btn-outline-secondary" disabled>
                <i class="fas fa-chevron-left"></i> Previous
            </button>
            {% endif %}

            <a href="{{ url_for('us_list') }}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-list"></i> Back to List
            </a>

            {% if next_id %}
            <a href="{{ url_for('edit_us', us_id=next_id) }}" class="btn btn-sm btn-outline-primary">
                Next <i class="fas fa-chevron-right"></i>
            </a>
            {% else %}
            <button class="btn btn-sm btn-outline-secondary" disabled>
                Next <i class="fas fa-chevron-right"></i>
            </button>
            {% endif %}
        </div>
    </div>
</div>
{% endif %}
```

### 3. Filtered PDF Export

#### Implementation Plan

**Modify `export_us_pdf()` route in `web_interface/app.py`**:

```python
@app.route('/export/us_pdf')
def export_us_pdf():
    """Export US list PDF with active filters"""
    from flask import session

    try:
        # Get filters from session
        filters = session.get('us_filters', {})

        # Build query filters
        query_filters = {}
        if filters.get('sito'):
            query_filters['sito'] = filters['sito']
        if filters.get('area'):
            query_filters['area'] = filters['area']
        if filters.get('unita_tipo'):
            query_filters['unita_tipo'] = filters['unita_tipo']
        if filters.get('anno_scavo'):
            query_filters['anno_scavo'] = int(filters['anno_scavo'])
        if filters.get('us_number'):
            query_filters['us'] = filters['us_number']

        # Get US data within session
        with db_manager.connection.get_session() as db_session:
            from pyarchinit_mini.models.us import US as USModel

            query = db_session.query(USModel)

            # Apply filters
            if query_filters.get('sito'):
                query = query.filter(USModel.sito == query_filters['sito'])
            if query_filters.get('area'):
                query = query.filter(USModel.area == query_filters['area'])
            if query_filters.get('unita_tipo'):
                query = query.filter(USModel.unita_tipo == query_filters['unita_tipo'])
            if query_filters.get('anno_scavo'):
                query = query.filter(USModel.anno_scavo == query_filters['anno_scavo'])
            if query_filters.get('us'):
                query = query.filter(USModel.us == query_filters['us'])

            us_records = query.limit(500).all()
            us_list = [us.to_dict() for us in us_records]

        if not us_list:
            flash('Nessuna US trovata con i filtri attuali', 'warning')
            return redirect(url_for('us_list'))

        # Generate PDF
        site_name_clean = filters.get('sito', 'Filtered_Results')

        # Create temporary file for PDF output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            output_path = tmp.name

        # Generate PDF to file
        pdf_generator.generate_us_pdf(site_name_clean, us_list, output_path)

        return send_file(output_path, as_attachment=True,
                       download_name=f"us_{site_name_clean}_filtered.pdf",
                       mimetype='application/pdf')

    except Exception as e:
        flash(f'Errore export PDF US: {str(e)}', 'error')
        return redirect(url_for('us_list'))
```

**Update Export Button in `web_interface/templates/us/list.html`**:

```html
<a href="{{ url_for('export_us_pdf') }}" class="btn btn-danger">
    <i class="fas fa-file-pdf"></i> {{ _('Export PDF') }}
    {% if total > 0 and total < us_service.count_us() %}
    <span class="badge bg-light text-dark">{{ total }} filtered</span>
    {% endif %}
</a>
```

### 4. Filtered Harris Matrix Export

#### Implementation Plan

**Create new route for filtered Harris Matrix**:

```python
@app.route('/export/harris_matrix_filtered')
@login_required
def export_harris_matrix_filtered():
    """Export Harris Matrix GraphML with active filters"""
    from flask import session

    try:
        # Get filters from session
        filters = session.get('us_filters', {})

        site_name = filters.get('sito')
        if not site_name:
            flash('Seleziona un sito per generare il Harris Matrix', 'warning')
            return redirect(url_for('us_list'))

        # Generate matrix for the site
        graph = matrix_generator.generate_matrix(site_name)

        # If filters are active, filter the graph nodes
        if any([filters.get('area'), filters.get('unita_tipo'), filters.get('anno_scavo')]):
            # Get filtered US list
            with db_manager.connection.get_session() as db_session:
                from pyarchinit_mini.models.us import US as USModel

                query = db_session.query(USModel).filter(USModel.sito == site_name)

                if filters.get('area'):
                    query = query.filter(USModel.area == filters['area'])
                if filters.get('unita_tipo'):
                    query = query.filter(USModel.unita_tipo == filters['unita_tipo'])
                if filters.get('anno_scavo'):
                    query = query.filter(USModel.anno_scavo == int(filters['anno_scavo']))

                filtered_us = query.all()
                filtered_us_numbers = [str(us.us) for us in filtered_us]

            # Create subgraph with only filtered nodes
            import networkx as nx
            filtered_graph = nx.DiGraph()

            for node in graph.nodes():
                node_us = str(node)
                if node_us in filtered_us_numbers:
                    filtered_graph.add_node(node, **graph.nodes[node])

            for u, v in graph.edges():
                if str(u) in filtered_us_numbers and str(v) in filtered_us_numbers:
                    filtered_graph.add_edge(u, v, **graph.edges[u, v])

            graph = filtered_graph

        # Export to GraphML
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
            temp_path = f.name

        result_path = matrix_generator.export_to_graphml(
            graph=graph,
            output_path=temp_path,
            site_name=site_name,
            title=f"{site_name} (Filtered)",
            reverse_epochs=False
        )

        if not result_path:
            flash('Errore durante l\'export GraphML', 'error')
            return redirect(url_for('us_list'))

        # Send file
        filename = f"{site_name}_harris_matrix_filtered.graphml"
        response = send_file(
            temp_path,
            mimetype='application/xml',
            as_attachment=True,
            download_name=filename
        )

        # Clean up temp file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(temp_path)
            except:
                pass

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Errore durante l\'export GraphML: {str(e)}', 'error')
        return redirect(url_for('us_list'))
```

**Add Export Button to `web_interface/templates/us/list.html`**:

```html
<div class="btn-group">
    <a href="{{ url_for('export_us_pdf') }}" class="btn btn-danger">
        <i class="fas fa-file-pdf"></i> {{ _('Export PDF') }}
    </a>
    {% if sito_filter %}
    <a href="{{ url_for('export_harris_matrix_filtered') }}" class="btn btn-success">
        <i class="fas fa-project-diagram"></i> {{ _('Export Matrix') }}
    </a>
    {% endif %}
</div>
```

### 5. Advanced Search for Inventory

#### Implementation Plan

Apply the same pattern as US:

1. **Modify `inventario_list()` route** - add filters for:
   - Site
   - Area
   - US
   - Find type (tipo_reperto)
   - Year
   - Conservation state

2. **Update `web_interface/templates/inventario/list.html`** - add filter card

3. **Modify `edit_inventario()` route** - add prev/next navigation

4. **Modify `export_inventario_pdf()` route** - apply session filters

## Testing Checklist

### Advanced Search
- [ ] Filter by site only
- [ ] Filter by multiple criteria
- [ ] Filter persistence across navigation
- [ ] Reset filters
- [ ] Results counter accuracy

### Record Navigation
- [ ] Previous button when not first record
- [ ] Next button when not last record
- [ ] Disabled state for first/last records
- [ ] Position counter accuracy
- [ ] Back to list button

### Filtered Exports
- [ ] PDF export with no filters
- [ ] PDF export with filters
- [ ] Matrix export with site filter
- [ ] Matrix export with area filter
- [ ] Matrix export with multiple filters

## User Benefits

1. **Faster Data Access**: Find specific records quickly with multi-field search
2. **Efficient Editing**: Navigate through filtered results without returning to list
3. **Targeted Exports**: Generate PDFs and matrices for specific subsets
4. **Better Workflow**: Maintain context when working with filtered data
5. **Reduced Clicks**: Navigate directly between records in detail view

## Implementation Priority

1. ⭐ **High Priority**: Record navigation (prev/next) - improves workflow significantly
2. ⭐ **High Priority**: Filtered PDF export - commonly requested feature
3. **Medium Priority**: Filtered Matrix export - useful for large sites
4. **Medium Priority**: Inventory advanced search - mirrors US functionality

## Next Steps

1. Complete record navigation implementation (code provided above)
2. Test navigation with various filter combinations
3. Implement filtered PDF export (code provided above)
4. Implement filtered Matrix export (code provided above)
5. Apply same pattern to Inventory module
6. Update user documentation
7. Create video tutorial for advanced search features

## Notes

- Session storage ensures filters persist across page navigation
- Large result sets (>500 records) may need pagination for PDF export
- Matrix filtering requires graph subgraph extraction
- Consider adding filter presets for common queries
- Add export format selection (PDF/Excel/CSV) to filter results

---

**Created**: 2025-10-26
**Last Updated**: 2025-10-26
**Status**: Implementation in progress