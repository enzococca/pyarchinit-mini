Stratigraphic Relationships
===========================

.. versionadded:: 1.2.16
   Corrected relationship labels for US and USM units

Overview
--------

PyArchInit-Mini uses the Extended Matrix Framework to represent complex stratigraphic relationships beyond traditional Harris Matrix. This system supports both traditional stratigraphic units (US, USM) and extended unit types (USVA, USVB, USVC, TU, USD, CON, VSF, SF, Extractor, Combiner, DOC, property).

Relationship Label Types
------------------------

The Extended Matrix Framework uses three types of relationship labels:

1. **Textual Labels** (for US and USM)
2. **Single Symbols** (for standard Extended Matrix units)
3. **Double Symbols** (for special Extended Matrix units)

US and USM - Textual Labels
----------------------------

.. versionchanged:: 1.2.16
   Fixed to use traditional textual relationship labels

Traditional stratigraphic units (US and USM) use **textual relationship labels** in both Italian and English:

Italian Labels
^^^^^^^^^^^^^^

* **Copre** - Covers (stratigraphic superposition)
* **Coperto da** - Covered by (inverse of Copre)
* **Taglia** - Cuts (truncation relationship)
* **Tagliato da** - Cut by (inverse of Taglia)
* **Riempie** - Fills (filling relationship)
* **Riempito da** - Filled by (inverse of Riempie)
* **Uguale a** - Same as/Equal to (contemporaneity)
* **Si lega a** - Bonds with (structural connection)
* **Si appoggia a** - Leans against (physical support)

English Labels
^^^^^^^^^^^^^^

* **Covers**
* **Covered by**
* **Cuts**
* **Cut by**
* **Fills**
* **Filled by**
* **Same as**
* **Equal to**
* **Bonds with**
* **Leans against**

Example
^^^^^^^

.. code-block:: python

   # Traditional Harris Matrix relationship
   US 1 --[Copre]--> US 2
   US 3 --[Taglia]--> US 1
   USM 5 --[Si appoggia a]--> USM 4

Visual Representation
^^^^^^^^^^^^^^^^^^^^^

In GraphML exports and Harris Matrix visualizations:

.. code-block:: text

   ┌────┐
   │US 1│
   └────┘
      │ Copre
      ↓
   ┌────┐
   │US 2│
   └────┘

Standard Extended Matrix Units
-------------------------------

Standard Extended Matrix unit types use **single arrow symbols**:

Unit Types
^^^^^^^^^^

* **USVA** - Virtual Stratigraphic Unit A
* **USVB** - Virtual Stratigraphic Unit B
* **USVC** - Virtual Stratigraphic Unit C
* **TU** - Temporal Unit
* **USD** - Documented Stratigraphic Unit
* **CON** - Container
* **VSF** - Virtual Stratigraphic Function
* **SF** - Stratigraphic Function

Relationship Symbols
^^^^^^^^^^^^^^^^^^^^

* **>** - Forward relationship (predecessor → successor)
* **<** - Backward relationship (successor ← predecessor)

Example
^^^^^^^

.. code-block:: python

   # Extended Matrix relationships with single symbols
   USVA 1 --[>]--> USVA 2
   TU 5 --[>]--> USD 3
   CON 10 --[>]--> SF 8

Visual Representation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   ┌──────┐
   │USVA 1│
   └──────┘
      │ >
      ↓
   ┌──────┐
   │USVA 2│
   └──────┘

Special Extended Matrix Units
------------------------------

Special Extended Matrix unit types use **double arrow symbols**:

Unit Types
^^^^^^^^^^

* **Extractor** - Data extraction node
* **Combiner** - Data combination node
* **DOC** - Documentation node
* **property** - Property/attribute node

Relationship Symbols
^^^^^^^^^^^^^^^^^^^^

* **>>** - Strong forward relationship
* **<<** - Strong backward relationship

Example
^^^^^^^

.. code-block:: python

   # Special units with double symbols
   Extractor 1 --[>>]--> US 5
   DOC 3 --[>>]--> Combiner 2
   property 7 --[>>]--> US 10

Visual Representation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   ┌───────────┐
   │Extractor 1│
   └───────────┘
        │ >>
        ↓
   ┌────┐
   │US 5│
   └────┘

Complete Example
----------------

Mixed Unit Types
^^^^^^^^^^^^^^^^

A complex stratigraphic sequence might include:

.. code-block:: python

   # Traditional stratigraphic relationships
   US 1 --[Copre]--> US 2
   US 3 --[Taglia]--> US 1
   USM 4 --[Si appoggia a]--> US 2

   # Extended Matrix units
   USVA 10 --[>]--> US 1
   TU 20 --[>]--> US 3

   # Special documentation nodes
   DOC 100 --[>>]--> US 1
   Extractor 200 --[>>]--> USVA 10

Visual Matrix
^^^^^^^^^^^^^

.. code-block:: text

   ┌─────────────┐
   │Extractor 200│
   └─────────────┘
         │ >>
         ↓
   ┌───────┐          ┌────────┐
   │USVA 10│───────>──│DOC 100 │
   └───────┘          └────────┘
      │ >                │ >>
      ↓                  ↓
   ┌────┐            ┌────┐
   │US 1│───Copre───>│US 2│
   └────┘            └────┘
      ↑ Taglia          ↑ Si appoggia a
      │                 │
   ┌────┐            ┌─────┐
   │US 3│            │USM 4│
   └────┘            └─────┘
      ↑ >
      │
   ┌─────┐
   │TU 20│
   └─────┘

Implementation Details
----------------------

Code Example
^^^^^^^^^^^^

The relationship label determination is handled in ``pyarchinit_visualizer.py``:

.. code-block:: python

   def _get_edge_label_for_unit(self, graph: nx.DiGraph, node: int, rel_type: str = '') -> str:
       """
       Get appropriate edge label based on unit type.

       Extended Matrix Framework Rules:
       - US and USM: Use traditional textual labels (e.g., "Copre", "Taglia")
       - USVA, USVB, USVC, TU, USD, CON, VSF, SF: Use single symbols (>, <)
       - Extractor, Combiner, DOC, property: Use double symbols (>>, <<)
       """
       node_data = graph.nodes[node]
       unita_tipo = node_data.get('unita_tipo', 'US')

       # US and USM use traditional textual relationship labels
       if unita_tipo in ['US', 'USM']:
           return rel_type if rel_type else 'Copre'

       # Special units use double symbols
       if unita_tipo in ['Extractor', 'Combiner', 'DOC', 'property']:
           return '>>'

       # Other Extended Matrix units use single symbol
       return '>'

Database Schema
^^^^^^^^^^^^^^^

Relationships are stored in the ``us_relationships_table``:

.. code-block:: sql

   CREATE TABLE us_relationships_table (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       sito VARCHAR(350) NOT NULL,
       us_from VARCHAR(100) NOT NULL,
       us_to VARCHAR(100) NOT NULL,
       relationship_type VARCHAR(50) NOT NULL,
       FOREIGN KEY (sito, us_from) REFERENCES us_table(sito, us),
       FOREIGN KEY (sito, us_to) REFERENCES us_table(sito, us)
   );

Relationship Types
^^^^^^^^^^^^^^^^^^

Valid relationship types depend on unit type:

**US/USM (Textual):**

.. code-block:: python

   VALID_RELATIONSHIPS = [
       'Copre', 'Coperto da',
       'Taglia', 'Tagliato da',
       'Riempie', 'Riempito da',
       'Uguale a', 'Si lega a', 'Si appoggia a',
       # English equivalents
       'Covers', 'Covered by',
       'Cuts', 'Cut by',
       'Fills', 'Filled by',
       'Same as', 'Equal to',
       'Bonds with', 'Leans against'
   ]

**Standard Extended Matrix (Symbols):**

.. code-block:: python

   STANDARD_SYMBOLS = ['>', '<']

**Special Extended Matrix (Double Symbols):**

.. code-block:: python

   SPECIAL_SYMBOLS = ['>>', '<<']

GraphML Export
--------------

Label Export Format
^^^^^^^^^^^^^^^^^^^

When exporting to GraphML for yEd:

.. code-block:: xml

   <!-- US to US with textual label -->
   <edge source="US_1" target="US_2">
       <data key="label">Copre</data>
       <data key="edgeType">stratigraphic</data>
   </edge>

   <!-- USVA to USVA with symbol -->
   <edge source="USVA_1" target="USVA_2">
       <data key="label">&gt;</data>
       <data key="edgeType">extended_matrix</data>
   </edge>

   <!-- DOC to US with double symbol -->
   <edge source="DOC_1" target="US_5">
       <data key="label">&gt;&gt;</data>
       <data key="edgeType">documentation</data>
   </edge>

Styling
^^^^^^^

Labels are styled differently based on type:

* **Textual labels**: Regular font, larger size
* **Single symbols**: Bold, medium size
* **Double symbols**: Bold, larger size, different color

Migration from Previous Versions
---------------------------------

Version 1.2.15 and Earlier
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 1.2.15
   All units used symbolic labels

In versions prior to 1.2.16, all units (including US and USM) incorrectly used symbolic labels (``>`` or ``>>``).

Migration Steps
^^^^^^^^^^^^^^^

Existing installations do not need data migration. The change only affects visualization and export:

1. **Harris Matrix Visualization**: Regenerate using new labels
2. **GraphML Exports**: Re-export for correct yEd visualization
3. **Database**: No changes required (relationship_type field unchanged)

Use Cases
---------

Archaeological Recording
^^^^^^^^^^^^^^^^^^^^^^^^

Traditional excavation recording:

.. code-block:: python

   # Layer sequence
   US 1 (Topsoil) --[Copre]--> US 2 (Medieval layer)
   US 2 --[Copre]--> US 3 (Roman layer)

   # Cut feature
   US 4 (Pit) --[Taglia]--> US 2
   US 4 --[Taglia]--> US 3

   # Wall relationships
   USM 10 (Wall) --[Si appoggia a]--> US 3

Complex Documentation
^^^^^^^^^^^^^^^^^^^^^

Advanced documentation with Extended Matrix:

.. code-block:: python

   # Core stratigraphic sequence
   US 1 --[Copre]--> US 2

   # Virtual aggregation
   USVA 100 --[>]--> US 1
   USVA 100 --[>]--> US 2

   # Documentation nodes
   DOC 200 --[>>]--> USVA 100

   # Property extraction
   Extractor 300 --[>>]--> DOC 200

API Usage
---------

Creating Relationships
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService

   us_service = USService(db_manager)

   # Traditional stratigraphic relationship
   us_service.add_relationship(
       sito='Pompei',
       us_from='1',
       us_to='2',
       relationship_type='Copre'
   )

   # Extended Matrix relationship is handled automatically
   # based on unit type

Querying Relationships
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get all relationships for a US
   relationships = us_service.get_relationships(
       sito='Pompei',
       us='1'
   )

   # Returns list of dictionaries:
   # [
   #     {'us_to': '2', 'relationship_type': 'Copre'},
   #     {'us_to': '5', 'relationship_type': 'Taglia'}
   # ]

Validation
----------

The system validates relationships based on unit type:

.. code-block:: python

   # Valid: US with textual label
   add_relationship('US', '1', '2', 'Copre')  # ✓

   # Invalid: US with symbol
   add_relationship('US', '1', '2', '>')      # ✗ Error

   # Valid: USVA with symbol
   add_relationship('USVA', '1', '2', '>')   # ✓

   # Invalid: USVA with textual label
   add_relationship('USVA', '1', '2', 'Copre')  # ✗ Error

See Also
--------

* :doc:`harris_matrix` - Harris Matrix visualization
* :doc:`graphml_export` - GraphML export for yEd
* :doc:`../data/stratigraphic_units` - US data model
* :doc:`/EXTENDED_MATRIX_FRAMEWORK` - Complete Extended Matrix documentation
