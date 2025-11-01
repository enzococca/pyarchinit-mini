# PyArchInit 3D Builder - User Guide

**Interactive 3D Stratigraphic Visualization with Blender Integration**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Creating Your First 3D Model](#creating-your-first-3d-model)
5. [Working with the 3D Viewer](#working-with-the-3d-viewer)
6. [Advanced Features](#advanced-features)
7. [Exporting and Sharing](#exporting-and-sharing)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

### What is the 3D Builder?

The 3D Builder is PyArchInit-Mini's powerful tool for creating interactive 3D visualizations of stratigraphic excavation data. Using natural language prompts, you can:

- Generate 3D models of stratigraphic sequences
- Visualize Harris Matrix relationships in 3D space
- Filter layers by chronological period
- Control visibility and transparency of individual units
- Export models for presentations and publications

### How It Works

```
┌─────────────────┐
│  You describe   │ "Create a 3D model showing Bronze Age
│  what you want  │  layers from Site 1"
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Claude AI      │ Interprets your request and queries
│  processes      │ the database
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Blender        │ Creates 3D geometry with proper
│  generates      │ spatial relationships
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Web Viewer     │ Interactive 3D visualization
│  displays       │ in your browser
└─────────────────┘
```

---

## Prerequisites

### Software Requirements

1. **PyArchInit-Mini** (v1.8.0 or higher)
   - Already installed if you're reading this

2. **Blender** (3.0 or higher)
   - Download from: https://www.blender.org/download/
   - Free and open source

3. **Modern Web Browser**
   - Chrome, Firefox, Safari, or Edge
   - WebGL support required

### Data Requirements

Before using the 3D Builder, you need:

- **Site data** with stratigraphic units (US) defined
- **Harris Matrix** created with relationships between units
- **(Optional)** Chronological periodization configured
- **(Optional)** Material finds associated with units

---

## Getting Started

### Step 1: Install Blender

1. Download Blender from https://www.blender.org/download/
2. Install following the instructions for your operating system
3. Launch Blender to verify it works

### Step 2: Install the PyArchInit Blender Addon

#### Method A: Automatic Installation (Recommended)

1. In PyArchInit web interface, navigate to:
   ```
   3D Builder > Setup > Install Blender Addon
   ```

2. Click **"Download Addon ZIP"**

3. In Blender:
   - Go to **Edit → Preferences → Add-ons**
   - Click **"Install..."** button
   - Select the downloaded `pyarchinit_mcp.zip` file
   - Enable the addon by checking the checkbox

#### Method B: Manual Installation

1. Locate the addon folder in PyArchInit:
   ```
   blender_addon/pyarchinit_mcp/
   ```

2. Copy it to Blender's addons directory:

   **macOS:**
   ```bash
   cp -r blender_addon/pyarchinit_mcp ~/Library/Application\ Support/Blender/3.x/scripts/addons/
   ```

   **Linux:**
   ```bash
   cp -r blender_addon/pyarchinit_mcp ~/.config/blender/3.x/scripts/addons/
   ```

   **Windows:**
   ```
   Copy blender_addon\pyarchinit_mcp to
   %APPDATA%\Blender Foundation\Blender\3.x\scripts\addons\
   ```

3. In Blender:
   - Go to **Edit → Preferences → Add-ons**
   - Search for "PyArchInit"
   - Enable **"3D View: PyArchInit MCP Connector"**

### Step 3: Start the Blender Server

1. **In Blender:**
   - Open the 3D Viewport
   - Press **N** to open the sidebar
   - Click the **"PyArchInit"** tab
   - Click **"Start Server"**

   You should see:
   ```
   Server Status: Running
   Port: 9876
   ```

2. **Test the Connection:**
   - In PyArchInit web interface:
   - Go to **3D Builder** page
   - Click **"Test Blender Connection"**
   - You should see a green "Connected" message

### Step 4: Configure Firewall (if needed)

If the connection test fails, you may need to allow port 9876:

**macOS:**
- System Preferences → Security & Privacy → Firewall → Firewall Options
- Add Blender to allowed applications

**Linux (ufw):**
```bash
sudo ufw allow 9876/tcp
```

**Windows:**
- Windows Defender Firewall → Advanced Settings → Inbound Rules
- Add rule for TCP port 9876

---

## Creating Your First 3D Model

### Basic Example

Let's create a simple 3D visualization of a stratigraphic sequence.

#### 1. Navigate to 3D Builder

In PyArchInit web interface:
- Click **"Harris Creator"** in the main menu
- Then click **"3D Builder"** tab

#### 2. Write Your Prompt

In the prompt box, describe what you want to visualize:

```
Create a 3D model of Site 1 showing all Bronze Age stratigraphic units
```

#### 3. Generate the Model

- Click **"Generate 3D Model"**
- Wait for processing (usually 10-30 seconds)
- The 3D viewer will appear with your model

#### 4. Explore the Model

- **Rotate:** Click and drag
- **Zoom:** Scroll mouse wheel
- **Pan:** Right-click and drag

### Understanding the Results

The generated model shows:

- **Cubes/Boxes:** Individual stratigraphic units (US)
- **Colors:** Represent chronological periods or material types
- **Vertical Position:** Stratigraphic relationships (higher = later)
- **Size:** Approximate extent of the unit

---

## Working with the 3D Viewer

### Viewer Interface

```
┌─────────────────────────────────────────────────┐
│  3D Viewer                          [⚙ Settings]│
├─────────────────────────────────────────────────┤
│                                                  │
│                  ┌───┐                          │
│                  │US5│  ← Latest layer          │
│           ┌───┐  └───┘                          │
│           │US3│    ↑                            │
│  ┌───┐   └───┘    │  Stratigraphic              │
│  │US1│      ↑     │  sequence                   │
│  └───┘      │     │                             │
│        Earlier layers                           │
│                                                  │
├─────────────────────────────────────────────────┤
│ Controls:  [⟲ Reset] [🔍 Fit] [💾 Export]      │
└─────────────────────────────────────────────────┘
```

### Navigation Controls

| Action | Mouse | Keyboard |
|--------|-------|----------|
| **Rotate** | Left click + drag | Arrow keys |
| **Zoom** | Scroll wheel | + / - |
| **Pan** | Right click + drag | Shift + arrows |
| **Reset View** | Click "Reset Camera" | Home |

### Proxy Information Panel

Click on any unit (cube) to see details:

```
┌─────────────────────────────┐
│ US 45 - Layer Information   │
├─────────────────────────────┤
│ Site: Pompeii - Regio VI    │
│ Type: Layer                 │
│ Period: Imperial Roman      │
│ Dating: 50-79 CE            │
│                             │
│ Description:                │
│ Volcanic ash layer from     │
│ 79 CE Vesuvius eruption     │
│                             │
│ Relationships:              │
│ ↑ Covers: US 46, US 47      │
│ ↓ Covered by: US 44         │
│                             │
│ Materials: 23 artifacts     │
│ Documentation: 5 photos     │
└─────────────────────────────┘
```

### Visibility Controls

Control which units are visible:

1. **By Period:**
   ```
   ☑ Bronze Age
   ☑ Iron Age
   ☐ Roman Period  ← Click to hide/show
   ☑ Medieval
   ```

2. **By Individual Unit:**
   - Click checkbox next to unit name in proxy list
   - Or use "Hide/Show All" buttons

### Transparency Control

Adjust transparency to see through layers:

```
Transparency: [════════░░] 80%
              ← Opaque    Transparent →
```

Use this to:
- Examine relationships between layers
- See occluded units
- Create clearer visualizations

### Color Coding

Units are colored by:

| Color | Period Example |
|-------|----------------|
| 🟫 Brown | Bronze Age |
| ⬛ Dark Gray | Iron Age |
| 🟥 Red | Roman |
| 🟦 Blue | Medieval |
| 🟩 Green | Modern |

Colors can be customized in the prompt or settings.

---

## Advanced Features

### Chronological Filtering

Filter the model by time period:

#### Using the Timeline Slider

```
Period Timeline
├──────┬──────┬──────┬──────┬──────┐
│Bronze│ Iron │Roman │Mediev│Modern│
│ Age  │ Age  │      │  al  │      │
└──────┴──────┴──────┴──────┴──────┘
     ↑              ↑
   [════════════════]

Show only: Bronze Age to Roman Period
```

Drag the slider handles to select date range.

#### Using Prompts

```
Show only layers from 1000-500 BCE

Filter to Imperial Roman period

Display medieval and later units
```

### Custom Visualizations

#### By Material Type

```
Create a 3D model showing layers with ceramic finds,
color them by ceramic type
```

#### By Excavation Area

```
Generate 3D view of Trench A and Trench B side by side,
highlighting the interface between them
```

#### By Depositional Process

```
Show natural layers in brown, anthropic layers in gray,
and destruction layers in red
```

### Spatial Relationships

#### Visualize Cuts and Fills

```
Create model of Site 2 showing all cut features (pits, ditches)
and their fills with different transparency
```

#### Show Interfaces

```
Display the contact surfaces between US 10 and its
contemporary units
```

### Harris Matrix Integration

Import relationships directly from Harris Matrix:

1. Create Harris Matrix in the Harris Creator
2. Export to GraphML format
3. In 3D Builder prompt:
   ```
   Import Harris Matrix from session "Excavation_2024"
   and create 3D visualization
   ```

---

## Exporting and Sharing

### Export 3D Model

#### glTF Format (Recommended)

1. Click **"Export Model"** button
2. Choose **glTF (.gltf)** format
3. File will download to your computer

**Use for:**
- Publishing on websites
- Sharing with collaborators
- Importing into other 3D software

#### Other Formats

- **OBJ:** For Meshlab, CloudCompare
- **FBX:** For Unity, Unreal Engine
- **STL:** For 3D printing

### Share Interactive View

Generate shareable link:

1. Click **"Share"** button
2. Choose sharing options:
   - ☑ Allow rotation/zoom
   - ☑ Show unit information
   - ☐ Allow editing
3. Copy link and send to collaborators

### Export Screenshots

Capture current view:

1. Adjust camera to desired angle
2. Click **"Screenshot"** button
3. Choose resolution:
   - 1920x1080 (HD)
   - 3840x2160 (4K)
   - Custom

### Create Animations

Generate turntable animation:

```
Create a 360-degree rotation animation of the current model
```

Output: MP4 video file (30 seconds, 30 fps)

---

## Troubleshooting

### Connection Issues

#### "Cannot connect to Blender"

**Solutions:**

1. **Verify Blender is running:**
   - Open Blender
   - Check server status in PyArchInit panel (N key → PyArchInit tab)

2. **Restart the server:**
   - In Blender, click "Stop Server"
   - Wait 5 seconds
   - Click "Start Server"

3. **Check firewall:**
   - Ensure port 9876 is allowed
   - Temporarily disable firewall to test

4. **Verify addon is enabled:**
   - Edit → Preferences → Add-ons
   - Search "PyArchInit"
   - Checkbox should be enabled

#### "Connection timeout"

**Solutions:**

1. **Increase timeout:**
   - In 3D Builder settings, increase timeout to 60 seconds

2. **Check system resources:**
   - Blender requires available memory
   - Close unnecessary applications

### Visualization Issues

#### "No units visible"

**Check:**

1. **Data exists:**
   - Verify you have US records in the database
   - Check Harris Matrix has relationships defined

2. **Filters:**
   - Click "Show All" button
   - Reset chronological filters

3. **Camera position:**
   - Click "Reset Camera" button
   - Try zooming out (scroll down)

#### "Units overlapping/misaligned"

**Solutions:**

1. **Refine the prompt:**
   ```
   Create 3D model with better vertical spacing between layers
   ```

2. **Manual adjustment:**
   - Select unit in proxy list
   - Adjust position in Blender (if advanced user)

#### "Wrong colors"

**Solutions:**

1. **Specify colors in prompt:**
   ```
   Create model with Bronze Age in brown and Iron Age in gray
   ```

2. **Check periodization:**
   - Ensure dating periods are configured correctly
   - Admin → Dating Periods

### Performance Issues

#### "Model generation is slow"

**For large datasets (>100 units):**

1. **Filter the data:**
   ```
   Create model showing only Bronze Age layers from Trench A
   ```

2. **Use batch processing:**
   - Generate models by period separately
   - Combine in Blender if needed

#### "Viewer is laggy"

**Solutions:**

1. **Reduce complexity:**
   - Hide unnecessary units
   - Use transparency instead of hiding

2. **Close other tabs/applications**

3. **Try a different browser:**
   - Chrome generally performs best
   - Ensure hardware acceleration is enabled

### Blender-specific Issues

#### "Addon won't enable"

**Check:**

1. **Blender version:**
   - Must be 3.0 or higher
   - Check: Help → About Blender

2. **Python version:**
   - Blender includes Python
   - Should be 3.7 or higher

3. **Installation path:**
   - Verify addon is in correct folder
   - See [Step 2](#step-2-install-the-pyarchinit-blender-addon)

#### "Server won't start"

**Solutions:**

1. **Port already in use:**
   - Change port in addon settings (default: 9876)
   - Try port 9877 or 9878

2. **Permissions:**
   - Run Blender as administrator (Windows)
   - Check file permissions (Linux/Mac)

3. **Check Blender console:**
   - Window → Toggle System Console (Windows)
   - Look for error messages

---

## FAQ

### General Questions

**Q: Do I need to keep Blender open all the time?**

A: Only when generating new models. Once a model is generated and exported, you can close Blender and still view it in the web interface.

**Q: Can multiple users use the same Blender instance?**

A: Yes, the Blender server can handle multiple concurrent requests from different PyArchInit users.

**Q: How many units can I visualize at once?**

A: Tested up to 500 units. Performance depends on your hardware. For very large sites, consider filtering by area or period.

**Q: Can I edit the 3D model after generation?**

A: Yes, advanced users can open the Blender file and make manual adjustments. The model will update in real-time in the web viewer.

### Data Questions

**Q: What if I don't have Harris Matrix relationships defined?**

A: The system will create a basic 3D layout based on stratigraphic sequence numbers. For best results, define relationships in the Harris Creator first.

**Q: Can I visualize finds/artifacts in 3D?**

A: Currently, the 3D Builder focuses on stratigraphic units. Artifact visualization is planned for future versions.

**Q: How does it handle complex relationships (like contemporaneous units)?**

A: Contemporary units are placed side-by-side at the same vertical level. The system interprets "same as" relationships from the Harris Matrix.

### Technical Questions

**Q: What 3D formats are supported for export?**

A: glTF, OBJ, FBX, DAE (Collada), STL, and X3D.

**Q: Can I use my own Blender scenes/templates?**

A: Yes, advanced users can customize the Blender template in the addon settings.

**Q: Is the data sent to external servers?**

A: No, all processing happens locally. Blender runs on your computer, and communication is entirely within your local network.

**Q: Can I run Blender on a different machine?**

A: Yes, configure the Blender host in 3D Builder settings. Both machines must be on the same network.

### Workflow Questions

**Q: What's the best workflow for large excavations?**

A:
1. Create separate models by excavation phase or area
2. Use chronological filtering to focus on specific periods
3. Export key views as glTF for publication
4. Keep Blender files for future adjustments

**Q: How do I integrate this with GIS data?**

A: Export the 3D model as OBJ or glTF, then import into QGIS with the Qgis2threejs plugin or similar tools.

**Q: Can I animate stratigraphic sequences?**

A: Yes, use prompts like:
```
Create an animation showing the depositional sequence
from earliest to latest layer
```

---

## Example Workflows

### Workflow 1: Basic Site Visualization

**Goal:** Create a simple 3D view of all excavation layers

1. **Prepare data:**
   - Enter US records with basic information
   - Define stratigraphic relationships in Harris Creator

2. **Generate model:**
   ```
   Create a 3D model of Site 1 showing all stratigraphic units
   ```

3. **Adjust view:**
   - Click "Reset Camera"
   - Adjust transparency to 70%
   - Hide modern/topsoil layers

4. **Export:**
   - Screenshot for excavation report
   - glTF file for website

### Workflow 2: Period-focused Analysis

**Goal:** Examine Bronze Age occupation layers

1. **Filter data:**
   ```
   Show only Bronze Age layers from Site 1,
   color by phase (Early, Middle, Late)
   ```

2. **Analyze relationships:**
   - Click on individual units to see details
   - Check which units are contemporary
   - Examine cutting relationships

3. **Refine:**
   ```
   Increase vertical spacing by 50% for better visibility
   ```

4. **Document:**
   - Take screenshots from multiple angles
   - Export model for 3D PDF in publication

### Workflow 3: Publication-ready Visualization

**Goal:** Create professional 3D figures for publication

1. **Generate base model:**
   ```
   Create detailed 3D model of Trench A with all Bronze Age
   and Iron Age layers, use earth-tone colors
   ```

2. **Refine visualization:**
   - Adjust camera angle for best view
   - Set transparency to highlight key features
   - Hide modern disturbances

3. **Add annotations:**
   - Use Blender text objects (advanced)
   - Or add labels in image editor after export

4. **Export high-resolution:**
   - Screenshot at 4K resolution
   - Export glTF for interactive supplementary material
   - Create turntable animation for presentation

### Workflow 4: Teaching and Outreach

**Goal:** Create interactive visualization for public engagement

1. **Generate accessible model:**
   ```
   Create a 3D model of the Roman villa excavation with
   simplified layers, using bright colors for each period
   ```

2. **Enable interaction:**
   - Share link with "Allow rotation" enabled
   - Add descriptions to each unit with plain language

3. **Create walkthrough:**
   - Record screen capture while explaining
   - Or generate narrated animation

---

## Best Practices

### Data Entry

1. **Consistent naming:** Use standard US numbering scheme
2. **Complete descriptions:** Fill in all relevant fields
3. **Define relationships:** Essential for proper 3D positioning
4. **Dating information:** Enables chronological filtering

### Prompts

1. **Be specific:**
   - ❌ "Make a 3D model"
   - ✅ "Create a 3D model of Site 1 showing Bronze Age layers"

2. **Specify colors if important:**
   - "Use brown for natural deposits, gray for occupation layers"

3. **Break complex requests into steps:**
   - First: Generate base model
   - Then: Adjust visibility and colors
   - Finally: Export

### Performance

1. **Start small:** Test with 10-20 units before visualizing entire site
2. **Use filters:** Don't try to show everything at once
3. **Progressive refinement:** Generate simple model first, then refine

### Organization

1. **Name sessions clearly:** "Site1_BronzeAge_2024"
2. **Save important views:** Export glTF files with descriptive names
3. **Document prompts:** Keep notes on successful prompt patterns

---

## Getting Help

### Resources

- **Technical Documentation:** See `3D_BUILDER_TECHNICAL_DOCUMENTATION.md` for developers
- **Blender Addon README:** See `blender_addon/pyarchinit_mcp/README.md`
- **PyArchInit Documentation:** https://pyarchinit.github.io/pyarchinit-mini

### Support Channels

- **Issues:** https://github.com/pyarchinit/pyarchinit-mini/issues
- **Community:** PyArchInit mailing list
- **Email:** [contact info]

### Reporting Bugs

When reporting issues, include:

1. **PyArchInit version:** Check Help → About
2. **Blender version:** Help → About Blender
3. **Operating system:** Windows/Mac/Linux + version
4. **Steps to reproduce:** What you did before the error
5. **Error messages:** Copy from browser console (F12)
6. **Blender console output:** Window → Toggle System Console

---

## Appendix A: Keyboard Shortcuts

### 3D Viewer

| Shortcut | Action |
|----------|--------|
| **Left Mouse** | Rotate view |
| **Right Mouse** | Pan view |
| **Scroll Wheel** | Zoom in/out |
| **Home** | Reset camera |
| **F** | Frame selected |
| **1-9** | Toggle layer visibility |
| **Spacebar** | Play/pause animation |
| **Ctrl+S** | Export screenshot |

### Blender (when editing)

| Shortcut | Action |
|----------|--------|
| **G** | Move selected object |
| **S** | Scale selected object |
| **R** | Rotate selected object |
| **X** | Delete selected object |
| **Shift+A** | Add new object |
| **Tab** | Toggle edit mode |
| **N** | Toggle properties panel |

---

## Appendix B: Prompt Examples

### Basic Prompts

```
Create a 3D model of Site 1
```

```
Show all stratigraphic units from Trench A
```

```
Generate 3D visualization of the Bronze Age sequence
```

### Filtering Prompts

```
Show only layers dating to 1000-500 BCE
```

```
Display layers with ceramic finds
```

```
Create model excluding modern disturbances
```

### Styling Prompts

```
Use brown for natural layers and gray for anthropic layers
```

```
Color units by excavation phase (Phase 1 in red, Phase 2 in blue)
```

```
Set transparency to 60% for better visibility of relationships
```

### Advanced Prompts

```
Create side-by-side view of Trench A and Trench B showing
the Bronze Age sequence with color coding by period
```

```
Generate 3D model with vertical exaggeration of 2x to
emphasize thin layers
```

```
Show the stratigraphic sequence with units colored by
soil composition (clay=brown, sand=yellow, gravel=gray)
```

### Animation Prompts

```
Create 360-degree turntable animation
```

```
Animate the depositional sequence from bottom to top
```

```
Show progressive excavation by phase
```

---

## Appendix C: Color Reference

### Default Period Colors

| Period | Hex Color | RGB | Visual |
|--------|-----------|-----|--------|
| Paleolithic | `#8B4513` | (139, 69, 19) | 🟫 Saddle Brown |
| Neolithic | `#A0522D` | (160, 82, 45) | 🟫 Sienna |
| Bronze Age | `#CD853F` | (205, 133, 63) | 🟫 Peru |
| Iron Age | `#696969` | (105, 105, 105) | ⬛ Dim Gray |
| Classical | `#8B0000` | (139, 0, 0) | 🟥 Dark Red |
| Roman | `#DC143C` | (220, 20, 60) | 🟥 Crimson |
| Medieval | `#4169E1` | (65, 105, 225) | 🟦 Royal Blue |
| Post-Medieval | `#32CD32` | (50, 205, 50) | 🟩 Lime Green |
| Modern | `#90EE90` | (144, 238, 144) | 🟩 Light Green |

### Material Type Colors

| Material | Hex Color | RGB | Visual |
|----------|-----------|-----|--------|
| Clay | `#B87333` | (184, 115, 51) | 🟫 Copper |
| Sand | `#F4A460` | (244, 164, 96) | 🟧 Sandy Brown |
| Gravel | `#A9A9A9` | (169, 169, 169) | ⬛ Dark Gray |
| Ash | `#DCDCDC` | (220, 220, 220) | ⬜ Gainsboro |
| Charcoal | `#2F4F4F` | (47, 79, 79) | ⬛ Dark Slate Gray |
| Limestone | `#F5F5DC` | (245, 245, 220) | ⬜ Beige |

---

## Appendix D: Glossary

**3D Proxy:** A simplified 3D object representing a stratigraphic unit in the visualization.

**glTF:** GL Transmission Format, a modern 3D file format optimized for web delivery.

**Harris Matrix:** A diagram showing the stratigraphic relationships between archaeological contexts.

**MCP (Model Context Protocol):** The communication protocol between PyArchInit and Blender.

**Server-Sent Events (SSE):** Technology for real-time updates from server to browser.

**Stratigraphic Unit (US):** A discrete archaeological layer or feature (from Italian "Unità Stratigrafica").

**Three.js:** JavaScript library for 3D graphics in web browsers.

**WebGL:** Web Graphics Library, browser technology for rendering 3D graphics.

---

## Changelog

### Version 1.8.0 (Current)
- Initial release of 3D Builder
- Blender MCP integration
- Real-time viewer with Three.js
- Chronological filtering
- GraphML import support
- Interactive controls (visibility, transparency)
- Export to glTF, OBJ, FBX

### Planned Features (v1.9.0)
- Artifact visualization in 3D space
- VR/AR support
- Collaborative editing
- Advanced lighting controls
- Automated camera paths
- Integration with photogrammetry models

---

**PyArchInit-Mini 3D Builder** | Archaeological 3D Visualization Made Simple

For technical documentation, see `3D_BUILDER_TECHNICAL_DOCUMENTATION.md`
