# Extended Matrix Node Type Management

**NEW in v1.6.0** - Extensible Configuration System for EM Node Types

## Overview

PyArchInit-Mini now features a flexible, user-friendly system for managing Extended Matrix node types. You can add custom node types without modifying code, using either:

1. **YAML Configuration File** - Direct file editing for power users
2. **Web Interface** - User-friendly GUI for managing node types (NEW!)

All node types are now defined in a central YAML configuration file that controls:
- Visual appearance (shapes, colors, fonts)
- Edge symbols (single/double arrows)
- Label formatting
- Validation rules

## Key Features

✅ **14 Built-in Node Types** - US, USM, VSF, SF, USD, USVA, USVB, USVC, TU, CON, DOC, property, Extractor, Combinar
✅ **Add Custom Types** - Create your own node types with custom styling
✅ **Web Interface** - Manage types through intuitive web UI
✅ **YAML Configuration** - Direct file editing for advanced users
✅ **Validation** - Automatic validation of colors, sizes, shapes
✅ **Hot Reload** - Changes take effect immediately

---

## Method 1: Web Interface (Recommended)

### Accessing the Interface

1. Start the web interface:
   ```bash
   cd web_interface
   python app.py
   ```

2. Navigate to: **http://localhost:5000/em-node-config**

3. Log in with your credentials

### Managing Node Types

#### Viewing Node Types

The interface displays all node types grouped by category:
- **Stratigraphic Units** - US, USM, VSF, etc. (use `>` / `<` symbols)
- **Non-Stratigraphic Units** - DOC, property, Extractor, etc. (use `>>` / `<<` symbols)

Each node type card shows:
- **Type ID** - Unique identifier (e.g., "US", "DOC")
- **Name** - Display name
- **Label Format** - Template for labels (e.g., "US{number}")
- **Symbol Type** - Single arrow (`>/<`) or double arrow (`>>/<<`)
- **Visual Style** - Shape, colors, font
- **Custom/Built-in Badge** - Custom types can be edited/deleted

#### Adding a Custom Node Type

1. Click **"Add Custom Node Type"** button
2. Fill in the form:

   **Basic Information:**
   - **Type ID**: Unique identifier (e.g., `USX`, `SAMPLE`) - uppercase recommended
   - **Name**: Display name (e.g., "Sample Unit")
   - **Description**: Optional description
   - **Category**: Stratigraphic or Non-Stratigraphic
   - **Symbol Type**: Single arrow (`>/<`) or double arrow (`>>/<<`)
   - **Label Format**: Template for node labels

   **Visual Style:**
   - **Shape**: rectangle, roundrectangle, hexagon, diamond, etc.
   - **Fill Color**: Interior color (hex color picker)
   - **Border Color**: Edge color (hex color picker)
   - **Border Width**: Edge thickness (0.1 - 10.0)
   - **Text Color**: Label text color
   - **Font Family**: DialogInput, Dialog, Arial, Helvetica
   - **Font Size**: 6 - 48
   - **Font Style**: plain, bold, italic, bolditalic

3. Click **"Save Node Type"**

#### Label Format Placeholders

- `{number}` - Replaced with US number (e.g., "US{number}" → "US1", "US2")
- `{first_word}` - Replaced with first word from description (e.g., for property nodes)

Examples:
```yaml
US{number}        → US1, US2, US3
D.{number}        → D.1, D.2, D.3
{first_word}      → Materiale, Material (from description)
SAMPLE-{number}   → SAMPLE-1, SAMPLE-2
```

#### Editing a Custom Node Type

1. Find the node type card (marked with "Custom" badge)
2. Click **"Edit"** button
3. Modify the fields
4. Click **"Save Node Type"**

**Note**: Built-in node types cannot be edited through the web interface.

#### Deleting a Custom Node Type

1. Find the node type card
2. Click **"Delete"** button
3. Confirm deletion

**Note**: Built-in node types cannot be deleted.

#### Reloading Configuration

Click **"Reload Config"** to reload the configuration from the YAML file. Useful after manual file edits.

---

## Method 2: YAML Configuration File

### Configuration File Location

```
pyarchinit_mini/config/em_node_types.yaml
```

### Configuration Structure

```yaml
version: "1.0"

node_types:
  US:  # Type ID
    name: "Stratigraphic Unit"
    description: "Standard stratigraphic unit"
    category: "stratigraphic"  # or "non_stratigraphic"
    symbol_type: "single_arrow"  # or "double_arrow"
    visual:
      shape: "rectangle"
      fill_color: "#FFFFFF"
      border_color: "#9B3333"
      border_width: 3.0
      width: 90.0
      height: 30.0
      font_family: "DialogInput"
      font_size: 24
      font_style: "bold"
      text_color: "#000000"
    label_format: "US{number}"

  # ... more node types ...

shapes:
  rectangle: "rectangle"
  roundrectangle: "roundrectangle"
  parallelogram: "parallelogram"
  hexagon: "hexagon"
  ellipse: "ellipse"
  triangle: "triangle"
  diamond: "diamond"
  octagon: "octagon"
  trapezoid: "trapezoid"
  bpmn_artifact: "bpmn_artifact"
  svg: "svg_node"

symbol_types:
  single_arrow:
    above: ">"
    below: "<"
    description: "Standard stratigraphic relationships"
  double_arrow:
    above: ">>"
    below: "<<"
    description: "Non-stratigraphic relationships"

defaults:
  fallback_type: "US"
  default_label_format: "US{number}"

validation:
  required_fields: [name, category, symbol_type, visual, label_format]
  valid_categories: [stratigraphic, non_stratigraphic]
  valid_symbol_types: [single_arrow, double_arrow]
  valid_shapes: [rectangle, roundrectangle, parallelogram, hexagon, ellipse, triangle, diamond, octagon, trapezoid, bpmn_artifact, svg]
  color_pattern: "^#[0-9A-Fa-f]{6}$"
  size_range:
    width: [10.0, 500.0]
    height: [10.0, 500.0]
    border_width: [0.1, 10.0]
```

### Adding a Custom Type via YAML

1. Open `pyarchinit_mini/config/em_node_types.yaml`
2. Add your custom type under `node_types`:

```yaml
node_types:
  # ... existing types ...

  SAMPLE:  # Your custom type ID
    name: "Sample Unit"
    description: "Custom sample unit type"
    category: "stratigraphic"
    symbol_type: "single_arrow"
    visual:
      shape: "diamond"
      fill_color: "#FFE6E6"
      border_color: "#CC0000"
      border_width: 2.5
      width: 100.0
      height: 40.0
      font_family: "Dialog"
      font_size: 14
      font_style: "bold"
      text_color: "#000000"
    label_format: "SAMPLE-{number}"
    custom: true  # Mark as custom type
```

3. Save the file
4. Reload the web interface or restart the application

### Validation Rules

The configuration manager automatically validates:

**Colors**:
- Must be hex format: `#RRGGBB` (e.g., `#FFFFFF`, `#9B3333`)

**Sizes**:
- Width: 10.0 - 500.0
- Height: 10.0 - 500.0
- Border Width: 0.1 - 10.0

**Required Fields**:
- `name`, `category`, `symbol_type`, `visual`, `label_format`

**Categories**:
- Must be `stratigraphic` or `non_stratigraphic`

**Symbol Types**:
- Must be `single_arrow` or `double_arrow`

**Shapes**:
- Must be one of the valid shapes defined in the configuration

---

## Python API

### Using the Configuration Manager

```python
from pyarchinit_mini.config.em_node_config_manager import get_config_manager

# Get global configuration manager instance
config = get_config_manager()

# Get all node types
all_types = config.get_all_node_types()

# Get specific node type
us_config = config.get_node_type('US')
print(us_config['name'])  # "Stratigraphic Unit"

# Get visual style for a type
visual = config.get_visual_style('USM')
print(visual['fill_color'])  # "#C0C0C0"

# Format a label
label = config.format_label('US', '123', '')
print(label)  # "US123"

# Get edge symbol for relationship direction
symbol = config.get_edge_symbol('US', 'above')
print(symbol)  # ">"

symbol = config.get_edge_symbol('DOC', 'below')
print(symbol)  # "<<"
```

### Adding Custom Types Programmatically

```python
from pyarchinit_mini.config.em_node_config_manager import get_config_manager

config = get_config_manager()

# Define visual style
visual = {
    'shape': 'hexagon',
    'fill_color': '#CCFFCC',
    'border_color': '#00AA00',
    'border_width': 2.0,
    'text_color': '#000000',
    'font_family': 'DialogInput',
    'font_size': 16,
    'font_style': 'bold',
    'width': 95.0,
    'height': 35.0
}

# Add custom node type
success = config.add_custom_node_type(
    tipo_id='FIND',
    name='Find Unit',
    description='Archaeological find',
    category='stratigraphic',
    symbol_type='single_arrow',
    visual=visual,
    label_format='FIND{number}'
)

if success:
    # Save to file
    config.save_config()
    print("Custom type added successfully!")
```

### Removing Custom Types

```python
from pyarchinit_mini.config.em_node_config_manager import get_config_manager, reset_config_manager

config = get_config_manager()

# Remove custom type
if config.remove_custom_node_type('FIND'):
    config.save_config()

    # Reset global manager to reload
    reset_config_manager()
    print("Custom type removed!")
```

---

## Architecture

### Components

1. **YAML Configuration File** (`pyarchinit_mini/config/em_node_types.yaml`)
   - Central definition of all node types
   - User-editable for power users
   - Version-controlled

2. **Configuration Manager** (`pyarchinit_mini/config/em_node_config_manager.py`)
   - `EMNodeConfigManager` class
   - Loads and validates configuration
   - Provides API for accessing/modifying types
   - Singleton pattern for global access

3. **EM Palette** (`pyarchinit_mini/graphml_converter/em_palette.py`)
   - Backward-compatible facade
   - Automatically uses configuration manager
   - Falls back to hardcoded styles if config unavailable

4. **Web Interface** (`web_interface/em_node_config_routes.py`)
   - Flask blueprint with REST API
   - CRUD operations for node types
   - User-friendly forms and validation

### Data Flow

```
User Action (Web UI or Direct YAML Edit)
           ↓
  YAML Config File Updated
           ↓
   Configuration Manager
           ↓
       EM Palette
           ↓
    GraphML Builder
           ↓
  yEd-compatible GraphML Export
```

---

## Use Cases

### Use Case 1: Adding a Custom Typological Unit

**Requirement**: Add "UTM" (Unit Tipologica Muraria - Typological Masonry Unit) with green styling.

**Via Web Interface**:
1. Go to http://localhost:5000/em-node-config
2. Click "Add Custom Node Type"
3. Fill in:
   - Type ID: `UTM`
   - Name: `Typological Masonry Unit`
   - Category: `stratigraphic`
   - Symbol Type: `single_arrow`
   - Label Format: `UTM{number}`
   - Shape: `roundrectangle`
   - Fill Color: `#E6FFE6` (light green)
   - Border Color: `#009900` (green)
4. Save

**Via YAML**:
```yaml
UTM:
  name: "Typological Masonry Unit"
  category: "stratigraphic"
  symbol_type: "single_arrow"
  visual:
    shape: "roundrectangle"
    fill_color: "#E6FFE6"
    border_color: "#009900"
    border_width: 3.0
    font_family: "DialogInput"
    font_size: 24
    font_style: "bold"
    text_color: "#000000"
  label_format: "UTM{number}"
  custom: true
```

### Use Case 2: Adding Photo Documentation Nodes

**Requirement**: Add "PHOTO" node type for photographic documentation.

**Configuration**:
```yaml
PHOTO:
  name: "Photograph"
  description: "Photographic documentation"
  category: "non_stratigraphic"
  symbol_type: "double_arrow"
  visual:
    shape: "bpmn_artifact"
    fill_color: "#FFFFCC"
    border_color: "#FFD700"
    border_width: 2.0
    font_family: "Dialog"
    font_size: 10
    font_style: "italic"
    text_color: "#000000"
  label_format: "PHOTO-{number}"
  custom: true
```

### Use Case 3: Custom Stratigraphic Interface

**Requirement**: Add "SI" (Stratigraphic Interface) with specific visual style.

**Via Web Interface**:
- Type ID: `SI`
- Name: `Stratigraphic Interface`
- Category: `stratigraphic`
- Symbol Type: `single_arrow`
- Shape: `parallelogram`
- Fill: Orange `#FFA500`
- Border: Dark orange `#FF8C00`
- Label Format: `SI{number}`

---

## Troubleshooting

### Configuration Not Loading

**Problem**: Changes to YAML file don't appear in exports.

**Solutions**:
1. Check YAML syntax (use online YAML validator)
2. Reload config via web interface (click "Reload Config")
3. Restart application
4. Check console for error messages

### Invalid Configuration Error

**Problem**: "Failed to create node type (validation failed)"

**Solutions**:
1. Verify color format is `#RRGGBB` (6 hex digits)
2. Check size ranges (width/height: 10-500, border: 0.1-10)
3. Ensure category is `stratigraphic` or `non_stratigraphic`
4. Verify symbol_type is `single_arrow` or `double_arrow`
5. Check shape is in list of valid shapes

### Custom Type Not Appearing

**Problem**: Added custom type via YAML but not showing in web interface.

**Solutions**:
1. Verify YAML syntax is correct
2. Check `custom: true` is set in the type definition
3. Clear browser cache
4. Click "Reload Config" button
5. Restart web server

### Permission Denied When Saving

**Problem**: Cannot save changes via web interface.

**Solutions**:
1. Check file permissions on `em_node_types.yaml`
2. Ensure web server has write access to config directory
3. Check user has write permissions (logged in with correct role)

---

## Best Practices

### Naming Conventions

- **Type IDs**: Use UPPERCASE (e.g., `US`, `DOC`, `SAMPLE`)
- **Names**: Use title case (e.g., "Stratigraphic Unit")
- **Descriptions**: Be concise but clear

### Color Selection

- **Stratigraphic Units**: Use earth tones (browns, grays, whites)
- **Virtual Units**: Use black fill with colored borders
- **Documentation**: Use light colors (yellows, light grays)
- **Properties**: Use very light fills with subtle borders

### Shape Selection

- **Standard Units**: Rectangle
- **Rounded Units**: Round Rectangle
- **Virtual Units**: Hexagon, Parallelogram
- **Destructive Units**: Round Rectangle with orange border
- **Documentation**: BPMN Artifact
- **Connectors**: SVG (diamond)

### Symbol Types

- **Stratigraphic Units**: Use `single_arrow` (`>` / `<`)
- **Non-Stratigraphic**: Use `double_arrow` (`>>` / `<<`)

### Label Formats

- Keep labels concise
- Use `{number}` for numeric identifiers
- Use `{first_word}` for descriptive labels
- Avoid overly long prefixes

---

## Changelog

### Version 1.6.0 (2025-10-28)

**New Features**:
- ✅ YAML-based configuration system for EM node types
- ✅ Web interface for managing node types (CRUD operations)
- ✅ Python API for programmatic access
- ✅ Automatic validation of colors, sizes, shapes
- ✅ Hot reload capability
- ✅ 14 built-in node types with full specifications

**Modified Components**:
- `EMPalette`: Now uses configuration manager as backend
- `GraphMLBuilder`: Automatically uses configured styles
- All export interfaces (CLI, Web, Desktop): Benefit from configuration system

**Files Added**:
- `pyarchinit_mini/config/em_node_types.yaml` - Configuration file
- `pyarchinit_mini/config/em_node_config_manager.py` - Manager class
- `web_interface/em_node_config_routes.py` - Web interface routes
- `web_interface/templates/em_node_config/index.html` - Web UI template
- `docs/EM_NODE_TYPE_MANAGEMENT.md` - This documentation

---

## Future Enhancements

### Planned Features

1. **SVG Upload**: Allow users to upload custom SVG symbols
2. **Color Palettes**: Predefined color schemes
3. **Import/Export**: Export custom types to share with other users
4. **Preview**: Real-time preview of node appearance
5. **Validation**: More advanced validation rules
6. **Desktop GUI**: Qt-based desktop interface for node management
7. **Templates**: Common node type templates

---

## Support

For questions or issues:

1. Check this documentation
2. Review YAML configuration file
3. Check web interface error messages
4. Open an issue on GitHub: https://github.com/pyarchinit/pyarchinit_mini/issues

---

**Author**: PyArchInit Development Team
**Last Updated**: 2025-10-28
**Version**: 1.6.0
