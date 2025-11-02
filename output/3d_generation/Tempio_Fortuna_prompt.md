# 3D Archaeological Reconstruction: Tempio Fortuna

## Context
You are an archaeological 3D reconstruction specialist. Your task is to create an accurate,
proportional 3D model of the **Tempio Fortuna** in Blender using the blender-mcp tools.

**Site Description:** Tempio romano dedicato alla dea Fortuna Primigenia, II sec. a.C.
**Location:** Palestrina, RM, Lazio, Italia

## Requirements

### 1. PHYSICAL UNITS (Excavated structures and layers)

Create these physical archaeological units with EXACT dimensions in meters:


**US 1000** - Strato superficiale
- Description: Terreno vegetale moderno
- Period: Contemporaneo to Contemporaneo
- Structure type: Layer
- Dimensions: 50.0m (L) × 45.0m (W) × 0.3m (H)
- Elevation: 450.3m a.s.l.
- Material: Bruno scuro, Sciolta
- Inclusions: None

**US 1001** - Strato di crollo
- Description: Crollo medievale del tetto
- Period: Medievale to Medievale
- Structure type: Layer
- Dimensions: 48.0m (L) × 42.0m (W) × 0.8m (H)
- Elevation: 450.0m a.s.l.
- Material: Grigio con laterizi, Compatta
- Inclusions: None

**US 1002** - Preparazione pavimentale
- Description: Preparazione pavimento opus sectile
- Period: Imperiale to Imperiale
- Structure type: Layer
- Dimensions: 45.0m (L) × 40.0m (W) × 0.2m (H)
- Elevation: 449.2m a.s.l.
- Material: Bianco calcareo, Molto compatta
- Inclusions: None

**US 1003** - Riempimento fondazione
- Description: Trincea fondazione tempio repubblicano
- Period: Repubblicano to Repubblicano
- Structure type: Layer
- Dimensions: 50.0m (L) × 5.0m (W) × 1.5m (H)
- Elevation: 449.0m a.s.l.
- Material: Bruno giallastro, Compatta
- Inclusions: None

**US 1004** - Deposito votivo
- Description: Oggetti votivi sotto pavimento
- Period: Repubblicano to Repubblicano
- Structure type: Layer
- Dimensions: 2.5m (L) × 2.0m (W) × 0.3m (H)
- Elevation: 448.8m a.s.l.
- Material: Rosso mattone con carboni, Sciolta
- Inclusions: None

**US 2001** - Muro perimetrale sud
- Description: Muro sud tempio repubblicano
- Period: Repubblicano to Repubblicano
- Structure type: Muro
- Dimensions: 30.0m (L) × 1.2m (W) × 2.5m (H)
- Elevation: 448.5m a.s.l.
- Material: Bianco calcare, Molto compatta
- Inclusions: Blocchi travertino, malta pozzolanica

**US 2002** - Muro perimetrale nord
- Description: Muro nord tempio, parzialmente distrutto
- Period: Repubblicano to Repubblicano
- Structure type: Muro
- Dimensions: 30.0m (L) × 1.2m (W) × 1.8m (H)
- Elevation: 448.5m a.s.l.
- Material: Bianco calcare, Compatta
- Inclusions: Blocchi travertino, lacune

**US 2003** - Muro est con basi coloniche
- Description: Muro est pronao con 4 basi corinzie
- Period: Repubblicano to Imperiale
- Structure type: Muro con elementi architettonici
- Dimensions: 20.0m (L) × 1.5m (W) × 2.0m (H)
- Elevation: 449.0m a.s.l.
- Material: Bianco calcare e marmo, Molto compatta
- Inclusions: Travertino, marmo lunense, basi attiche

**US 2004** - Muro ovest della cella
- Description: Muro di fondo cella, tracce affreschi
- Period: Repubblicano to Imperiale
- Structure type: Muro
- Dimensions: 15.0m (L) × 1.0m (W) × 3.0m (H)
- Elevation: 450.0m a.s.l.
- Material: Bianco con tracce rosse, Molto compatta
- Inclusions: Travertino, intonaco dipinto

**US 2005** - Fusti colonici crollati
- Description: Frammenti in situ colonne pronao
- Period: Repubblicano to Repubblicano
- Structure type: Elemento architettonico frammentario
- Dimensions: 4.5m (L) × 1.2m (W) × 1.2m (H)
- Elevation: 449.5m a.s.l.
- Material: Bianco marmoreo, Molto compatta
- Inclusions: Marmo lunense, scanalature

**US 2006** - Rifacimento medievale
- Description: Muro reimpiego materiali romani
- Period: Medievale to Medievale
- Structure type: Muro
- Dimensions: 8.0m (L) × 0.8m (W) × 1.5m (H)
- Elevation: 449.8m a.s.l.
- Material: Misto, Mediamente compatta
- Inclusions: Materiale reimpiego, malta calce

**US 2007** - Restauro moderno
- Description: Integrazione cemento 1965
- Period: Contemporaneo to Contemporaneo
- Structure type: Integrazione
- Dimensions: 5.0m (L) × 1.2m (W) × 1.0m (H)
- Elevation: 449.0m a.s.l.
- Material: Grigio cemento, Molto compatta
- Inclusions: Cemento Portland, rete metallica


### 2. RECONSTRUCTION NODES (Virtual 3D reconstructions)

Create these hypothetical reconstructions based on archaeological evidence:


**EM 3001** - Ricostruzione virtuale completa del tempio
- Description: Ricostruzione 3D completa basata su US 2001-2005. Include pronao esastilo, cella, podio e scalinata frontale.
- Period: Repubblicano
- Observations: Base archeologica: USM 2001-2004 (muri perimetrali), USM 2003 (basi colonne), confronti con Tempio B Largo Argentina

**EM 3002** - Ricostruzione copertura lignea
- Description: Copertura a doppio spiovente con travature in abete, coppi e tegole. Altezza colmo: ~12m
- Period: Repubblicano
- Observations: Basato su US 1001 (crollo medievale tegole), confronti tipologici

**EM 3003** - Ricostruzione colonne pronao
- Description: Sei colonne frontali corinzie in marmo lunense, h. ~8m, diametro base 1.2m. Capitelli con foglie d'acanto.
- Period: Repubblicano
- Observations: Basato su USM 2005 (fusti crollati), USM 2003 (basi in situ), rapporti metrici ordini corinzi canonici


### 3. MATERIALS AND TEXTURES

Apply realistic materials based on period and construction:

- **Republican period (II BC)**: Travertine stone (white-cream), pozzolanic mortar
- **Imperial period (I-II AD)**: Marble (white Carrara marble), colored opus sectile
- **Medieval period**: Reused Roman materials, lime mortar
- **Modern restoration**: Concrete (grey), steel reinforcement

### 4. SPATIAL ORGANIZATION

- Use absolute elevations (m a.s.l.) for Z-axis positioning
- Oldest layers at bottom (lowest elevation)
- Walls vertical, layers horizontal
- Maintain proportions between elements

### 5. VALIDATION CRITERIA

Your 3D model must:
✓ Use EXACT dimensions from the data (in meters)
✓ Respect stratigraphic relationships (lower = older)
✓ Apply period-appropriate materials
✓ Maintain architectural proportions
✓ Position elements at correct absolute elevations

## Instructions

1. **Clear the scene** - Remove default cube, camera, light
2. **Create physical units** - Build all excavated structures (US 1000-2007)
3. **Add reconstructions** - Create hypothetical elements (EM 3001-3003)
4. **Apply materials** - Assign realistic textures and colors
5. **Position correctly** - Use elevations for vertical placement
6. **Add lighting** - Studio lighting to showcase the reconstruction
7. **Set camera** - Isometric view showing the entire temple

## Expected Output

A complete 3D model of the **Temple of Fortuna** showing:
- Excavated foundations and walls (Republican period)
- Stratigraphic layers in section
- Virtual reconstruction of missing elements (roof, columns)
- Clear visual distinction between excavated and reconstructed parts
- Accurate scale and proportions (temple approx. 30m × 20m)

**Start by creating the foundation and perimeter walls (USM 2001-2004), then build upward layer by layer.**
