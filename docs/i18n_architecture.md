# Internationalization (i18n) Architecture for PyArchInit-Mini

## Overview

This document describes the internationalization implementation for PyArchInit-Mini, supporting Italian (default) and English.

## Technology Stack

- **Flask-Babel**: For Flask web interface
- **gettext**: Standard GNU translation system
- **Database**: Separate columns for translations (`field_it`, `field_en`)
- **Code**: English naming conventions with Italian/English UI translations

## Architecture Design

### 1. Translation File Structure

```
pyarchinit_mini/
├── translations/
│   ├── it/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po    # Italian translations
│   │       └── messages.mo    # Compiled Italian translations
│   └── en/
│       └── LC_MESSAGES/
│           ├── messages.po    # English translations
│           └── messages.mo    # Compiled English translations
├── babel.cfg                  # Babel extraction configuration
└── locales.py                 # Locale configuration and utilities
```

### 2. Flask-Babel Configuration

**File**: `web_interface/app.py`

```python
from flask_babel import Babel, gettext, lazy_gettext

def get_locale():
    """Determine user's preferred language from:
    1. URL parameter (?lang=en)
    2. Session
    3. Cookie
    4. Browser Accept-Language header
    5. Default to Italian
    """
    # URL parameter
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')

    # Session or Cookie
    if 'lang' in session:
        return session['lang']

    # Browser header
    return request.accept_languages.best_match(['it', 'en']) or 'it'

# Initialize Babel
babel = Babel(app, locale_selector=get_locale)

# Configure Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'it'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../pyarchinit_mini/translations'
```

### 3. Database Schema Changes

#### 3.1 Site Table (site_table)

**Migration**: Add English columns for translatable fields

```sql
-- Current Italian columns remain
ALTER TABLE site_table ADD COLUMN definizione_sito_en VARCHAR;
ALTER TABLE site_table ADD COLUMN descrizione_en TEXT;
```

**SQLAlchemy Model** (`models/site.py`):

```python
from sqlalchemy import Column, String, Text

class Site(Base):
    __tablename__ = 'site_table'

    # Primary identification (language-neutral)
    sito = Column(String, primary_key=True)
    nazione = Column(String)
    regione = Column(String)
    comune = Column(String)
    provincia = Column(String)
    sito_path = Column(String)
    find_check = Column(Integer)

    # Translatable fields (Italian + English)
    definizione_sito_it = Column(String)  # Rename from definizione_sito
    definizione_sito_en = Column(String)
    descrizione_it = Column(Text)         # Rename from descrizione
    descrizione_en = Column(Text)

    @property
    def definizione_sito(self):
        """Get site definition in current locale"""
        from flask import has_request_context
        if has_request_context():
            from flask_babel import get_locale
            locale = str(get_locale())
            return getattr(self, f'definizione_sito_{locale}', self.definizione_sito_it)
        return self.definizione_sito_it

    @property
    def descrizione(self):
        """Get description in current locale"""
        from flask import has_request_context
        if has_request_context():
            from flask_babel import get_locale
            locale = str(get_locale())
            return getattr(self, f'descrizione_{locale}', self.descrizione_it)
        return self.descrizione_it
```

#### 3.2 US Table (us_table)

**Fields requiring translation** (subjective/descriptive only):

```sql
-- Type and interpretation fields
ALTER TABLE us_table ADD COLUMN d_stratigrafica_en VARCHAR;
ALTER TABLE us_table ADD COLUMN d_interpretativa_en VARCHAR;

-- Physical description fields
ALTER TABLE us_table ADD COLUMN formazione_en VARCHAR;
ALTER TABLE us_table ADD COLUMN stato_di_conservazione_en VARCHAR;
ALTER TABLE us_table ADD COLUMN colore_en VARCHAR;
ALTER TABLE us_table ADD COLUMN consistenza_en VARCHAR;
ALTER TABLE us_table ADD COLUMN struttura_en VARCHAR;

-- Documentation fields
ALTER TABLE us_table ADD COLUMN inclusi_en TEXT;
ALTER TABLE us_table ADD COLUMN campioni_en TEXT;
ALTER TABLE us_table ADD COLUMN documentazione_en TEXT;
```

**Note**: Technical fields like `us` (number), `area`, `anno_scavo`, measurements remain language-neutral.

#### 3.3 Inventario Table (inventario_materiali_table)

```sql
-- Classification fields
ALTER TABLE inventario_materiali_table ADD COLUMN tipo_reperto_en VARCHAR;
ALTER TABLE inventario_materiali_table ADD COLUMN definizione_en VARCHAR;
ALTER TABLE inventario_materiali_table ADD COLUMN elementi_reperto_en TEXT;

-- Physical state
ALTER TABLE inventario_materiali_table ADD COLUMN stato_conservazione_en VARCHAR;

-- Ceramic specific
ALTER TABLE inventario_materiali_table ADD COLUMN corpo_ceramico_en VARCHAR;
ALTER TABLE inventario_materiali_table ADD COLUMN rivestimento_en VARCHAR;
ALTER TABLE inventario_materiali_table ADD COLUMN tipo_contenitore_en VARCHAR;
```

#### 3.4 Migration Script

**File**: `pyarchinit_mini/database/migrations/add_i18n_columns.py`

```python
"""
Add internationalization columns (_en) to all tables
"""

def upgrade(connection):
    """Add _en columns for translatable fields"""

    # Site table
    connection.execute("""
        ALTER TABLE site_table
        ADD COLUMN definizione_sito_en VARCHAR,
        ADD COLUMN descrizione_en TEXT
    """)

    # Rename existing columns to _it
    connection.execute("""
        ALTER TABLE site_table
        RENAME COLUMN definizione_sito TO definizione_sito_it,
        RENAME COLUMN descrizione TO descrizione_it
    """)

    # US table
    connection.execute("""
        ALTER TABLE us_table
        ADD COLUMN d_stratigrafica_en VARCHAR,
        ADD COLUMN d_interpretativa_en VARCHAR,
        ADD COLUMN formazione_en VARCHAR,
        ADD COLUMN stato_di_conservazione_en VARCHAR,
        ADD COLUMN colore_en VARCHAR,
        ADD COLUMN consistenza_en VARCHAR,
        ADD COLUMN struttura_en VARCHAR,
        ADD COLUMN inclusi_en TEXT,
        ADD COLUMN campioni_en TEXT,
        ADD COLUMN documentazione_en TEXT
    """)

    # Rename existing columns to _it
    connection.execute("""
        ALTER TABLE us_table
        RENAME COLUMN d_stratigrafica TO d_stratigrafica_it,
        RENAME COLUMN d_interpretativa TO d_interpretativa_it,
        RENAME COLUMN formazione TO formazione_it,
        RENAME COLUMN stato_di_conservazione TO stato_di_conservazione_it,
        RENAME COLUMN colore TO colore_it,
        RENAME COLUMN consistenza TO consistenza_it,
        RENAME COLUMN struttura TO struttura_it,
        RENAME COLUMN inclusi TO inclusi_it,
        RENAME COLUMN campioni TO campioni_it,
        RENAME COLUMN documentazione TO documentazione_it
    """)

    # Inventario table
    connection.execute("""
        ALTER TABLE inventario_materiali_table
        ADD COLUMN tipo_reperto_en VARCHAR,
        ADD COLUMN definizione_en VARCHAR,
        ADD COLUMN elementi_reperto_en TEXT,
        ADD COLUMN stato_conservazione_en VARCHAR,
        ADD COLUMN corpo_ceramico_en VARCHAR,
        ADD COLUMN rivestimento_en VARCHAR,
        ADD COLUMN tipo_contenitore_en VARCHAR
    """)

def downgrade(connection):
    """Remove _en columns and rename _it columns back"""
    # Revert changes
    pass
```

### 4. Code Refactoring: Italian to English

#### 4.1 Variable Naming Convention

**Before** (Italian):
```python
def crea_sito(dati):
    nuovo_sito = Site(
        sito=dati['sito'],
        nazione=dati['nazione'],
        descrizione=dati['descrizione']
    )
    return nuovo_sito
```

**After** (English with i18n):
```python
def create_site(data):
    """Create new archaeological site

    Args:
        data: Site data with IT/EN fields
    """
    new_site = Site(
        sito=data['sito'],  # Site code is language-neutral
        nazione=data['nazione'],
        descrizione_it=data.get('descrizione_it'),
        descrizione_en=data.get('descrizione_en')
    )
    return new_site
```

#### 4.2 Method Renaming Map

**Services** (`services/*.py`):

| Italian (Old) | English (New) | File |
|---------------|---------------|------|
| `crea_sito()` | `create_site()` | site_service.py |
| `aggiorna_sito()` | `update_site()` | site_service.py |
| `elimina_sito()` | `delete_site()` | site_service.py |
| `ottieni_tutti_siti()` | `get_all_sites()` | site_service.py |
| `crea_us()` | `create_stratigraphic_unit()` | us_service.py |
| `aggiorna_us()` | `update_stratigraphic_unit()` | us_service.py |
| `crea_inventario()` | `create_inventory_item()` | inventario_service.py |

**Database Manager** (`database/manager.py`):

| Italian (Old) | English (New) |
|---------------|---------------|
| `crea_record()` | `create_record()` |
| `aggiorna_record()` | `update_record()` |
| `elimina_record()` | `delete_record()` |
| `ottieni_record()` | `get_record()` |

### 5. Web Interface i18n

#### 5.1 Template Translation

**Before** (`templates/sites/list.html`):
```html
<h1>Elenco Siti Archeologici</h1>
<table>
    <thead>
        <tr>
            <th>Sito</th>
            <th>Nazione</th>
            <th>Descrizione</th>
        </tr>
    </thead>
</table>
```

**After** (with Babel):
```html
<h1>{{ _('Archaeological Sites List') }}</h1>
<table>
    <thead>
        <tr>
            <th>{{ _('Site') }}</th>
            <th>{{ _('Country') }}</th>
            <th>{{ _('Description') }}</th>
        </tr>
    </thead>
</table>
```

#### 5.2 WTForms Translation

**Before** (`web_interface/forms.py`):
```python
class SiteForm(FlaskForm):
    sito = StringField('Sito', validators=[DataRequired()])
    nazione = StringField('Nazione')
    descrizione = TextAreaField('Descrizione')
```

**After** (with lazy_gettext):
```python
from flask_babel import lazy_gettext as _l

class SiteForm(FlaskForm):
    sito = StringField(_l('Site'), validators=[DataRequired()])
    nazione = StringField(_l('Country'))
    descrizione_it = TextAreaField(_l('Description (IT)'))
    descrizione_en = TextAreaField(_l('Description (EN)'))

    submit = SubmitField(_l('Save'))
```

#### 5.3 Language Switcher Component

**File**: `templates/components/language_switcher.html`

```html
<div class="language-switcher">
    <a href="{{ url_for(request.endpoint, lang='it', **request.view_args) }}"
       class="{% if get_locale() == 'it' %}active{% endif %}">
        <img src="/static/flags/it.svg" alt="Italiano"> IT
    </a>
    <a href="{{ url_for(request.endpoint, lang='en', **request.view_args) }}"
       class="{% if get_locale() == 'en' %}active{% endif %}">
        <img src="/static/flags/en.svg" alt="English"> EN
    </a>
</div>
```

Include in `base.html`:
```html
<nav>
    <!-- ... existing nav items ... -->
    {% include 'components/language_switcher.html' %}
</nav>
```

### 6. Desktop GUI i18n

#### 6.1 Translation Module

**File**: `desktop_gui/i18n.py`

```python
import gettext
import locale
import os
from pathlib import Path

class DesktopI18n:
    """Desktop GUI internationalization manager"""

    def __init__(self):
        self.current_locale = 'it'
        self.localedir = Path(__file__).parent.parent / 'pyarchinit_mini' / 'translations'
        self._translator = None
        self.load_locale()

    def load_locale(self, lang=None):
        """Load translations for specified language"""
        if lang:
            self.current_locale = lang

        try:
            self._translator = gettext.translation(
                'messages',
                localedir=str(self.localedir),
                languages=[self.current_locale],
                fallback=True
            )
        except Exception as e:
            print(f"Translation loading error: {e}")
            self._translator = gettext.NullTranslations()

    def _(self, message):
        """Translate message to current locale"""
        return self._translator.gettext(message)

    def switch_language(self, lang):
        """Switch interface language"""
        self.load_locale(lang)

# Global instance
i18n = DesktopI18n()
_ = i18n._
```

#### 6.2 GUI Widget Translation

**Before** (`desktop_gui/main_window.py`):
```python
menu_file = tk.Menu(menubar, tearoff=0)
menu_file.add_command(label="Nuovo Sito", command=self.new_site)
menu_file.add_command(label="Apri", command=self.open_site)
menubar.add_cascade(label="File", menu=menu_file)
```

**After** (with i18n):
```python
from desktop_gui.i18n import _

menu_file = tk.Menu(menubar, tearoff=0)
menu_file.add_command(label=_("New Site"), command=self.new_site)
menu_file.add_command(label=_("Open"), command=self.open_site)
menubar.add_cascade(label=_("File"), menu=menu_file)
```

#### 6.3 Language Switcher Menu

```python
def create_language_menu(self):
    """Add language selection to menu"""
    lang_menu = tk.Menu(self.menubar, tearoff=0)

    lang_var = tk.StringVar(value=i18n.current_locale)

    lang_menu.add_radiobutton(
        label="Italiano",
        variable=lang_var,
        value="it",
        command=lambda: self.switch_language("it")
    )
    lang_menu.add_radiobutton(
        label="English",
        variable=lang_var,
        value="en",
        command=lambda: self.switch_language("en")
    )

    self.menubar.add_cascade(label=_("Language"), menu=lang_menu)

def switch_language(self, lang):
    """Switch GUI language and refresh"""
    i18n.switch_language(lang)
    messagebox.showinfo(
        _("Language Changed"),
        _("Please restart the application for changes to take effect.")
    )
```

### 7. REST API i18n

#### 7.1 Accept-Language Header Support

**File**: `pyarchinit_mini/api/dependencies.py`

```python
from fastapi import Header
from typing import Optional

def get_locale(accept_language: Optional[str] = Header(None)) -> str:
    """Extract locale from Accept-Language header

    Examples:
        Accept-Language: it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7
    """
    if not accept_language:
        return 'it'

    # Parse Accept-Language header
    languages = []
    for lang in accept_language.split(','):
        if ';q=' in lang:
            locale, quality = lang.split(';q=')
            languages.append((locale.strip(), float(quality)))
        else:
            languages.append((lang.strip(), 1.0))

    # Sort by quality
    languages.sort(key=lambda x: x[1], reverse=True)

    # Return first supported language
    for locale, _ in languages:
        lang_code = locale.split('-')[0]
        if lang_code in ['it', 'en']:
            return lang_code

    return 'it'
```

#### 7.2 Response Schemas with Translations

**File**: `pyarchinit_mini/api/schemas.py`

```python
from pydantic import BaseModel, Field

class SiteResponse(BaseModel):
    """Site response with localized fields"""
    sito: str = Field(..., description="Site code (language-neutral)")
    nazione: str
    regione: str

    # Localized fields
    definizione_sito: Optional[str] = Field(None, description="Site definition in current locale")
    descrizione: Optional[str] = Field(None, description="Description in current locale")

    # Raw translations (optional for editing)
    definizione_sito_it: Optional[str]
    definizione_sito_en: Optional[str]
    descrizione_it: Optional[str]
    descrizione_en: Optional[str]

    class Config:
        orm_mode = True
```

#### 7.3 API Endpoint Example

**File**: `pyarchinit_mini/api/site.py`

```python
from fastapi import APIRouter, Depends
from typing import List
from .dependencies import get_locale

router = APIRouter()

@router.get("/sites", response_model=List[SiteResponse])
async def get_sites(
    locale: str = Depends(get_locale),
    db: DatabaseManager = Depends(get_db)
):
    """Get all sites with localized fields"""
    sites = db.get_all_sites()

    # Set localized fields based on locale
    for site in sites:
        site.definizione_sito = getattr(site, f'definizione_sito_{locale}', site.definizione_sito_it)
        site.descrizione = getattr(site, f'descrizione_{locale}', site.descrizione_it)

    return sites
```

### 8. CLI i18n

**File**: `cli_interface/cli_app.py`

```python
import gettext
from pathlib import Path

# Setup gettext
localedir = Path(__file__).parent.parent / 'pyarchinit_mini' / 'translations'
translator = gettext.translation('messages', localedir=str(localedir), languages=['it'], fallback=True)
_ = translator.gettext

# CLI can switch language with environment variable
import os
cli_lang = os.getenv('PYARCHINIT_LANG', 'it')
translator = gettext.translation('messages', localedir=str(localedir), languages=[cli_lang], fallback=True)
_ = translator.gettext

# Usage in CLI
console.print(f"[bold]{_('Archaeological Sites Management')}[/bold]")
```

### 9. GraphML Export i18n

**File**: `pyarchinit_mini/graphml_converter/graphml_exporter.py`

```python
def export_to_graphml(dot_graph, locale='it'):
    """Export graph to GraphML with localized labels

    Args:
        dot_graph: Parsed DOT graph
        locale: 'it' or 'en' for node labels
    """
    for node in graph.nodes():
        node_data = graph.nodes[node]

        # Get localized description
        if 'd_interpretativa_it' in node_data:
            if locale == 'en' and 'd_interpretativa_en' in node_data:
                description = node_data['d_interpretativa_en']
            else:
                description = node_data['d_interpretativa_it']

            node_data['description'] = description
```

### 10. Translation Extraction Workflow

#### 10.1 babel.cfg Configuration

**File**: `pyarchinit_mini/babel.cfg`

```ini
[python: **.py]
[jinja2: **/templates/**.html]
encoding = utf-8
```

#### 10.2 Extract Translatable Strings

```bash
# Extract messages from Python and Jinja2 files
pybabel extract -F pyarchinit_mini/babel.cfg -o pyarchinit_mini/translations/messages.pot .

# Initialize Italian catalog
pybabel init -i pyarchinit_mini/translations/messages.pot -d pyarchinit_mini/translations -l it

# Initialize English catalog
pybabel init -i pyarchinit_mini/translations/messages.pot -d pyarchinit_mini/translations -l en

# Update catalogs after adding new strings
pybabel update -i pyarchinit_mini/translations/messages.pot -d pyarchinit_mini/translations

# Compile translations to .mo files
pybabel compile -d pyarchinit_mini/translations
```

#### 10.3 Translation File Example

**File**: `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po`

```po
# Italian translations for PyArchInit-Mini
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Language: it\n"

msgid "Archaeological Sites List"
msgstr "Elenco Siti Archeologici"

msgid "Site"
msgstr "Sito"

msgid "Country"
msgstr "Nazione"

msgid "Description"
msgstr "Descrizione"

msgid "New Site"
msgstr "Nuovo Sito"

msgid "Edit Site"
msgstr "Modifica Sito"

msgid "Delete Site"
msgstr "Elimina Sito"

# Stratigraphic Units
msgid "Stratigraphic Unit"
msgstr "Unità Stratigrafica"

msgid "Formation"
msgstr "Formazione"

msgid "State of Conservation"
msgstr "Stato di Conservazione"
```

**File**: `pyarchinit_mini/translations/en/LC_MESSAGES/messages.po`

```po
# English translations for PyArchInit-Mini
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Language: en\n"

msgid "Archaeological Sites List"
msgstr "Archaeological Sites List"

msgid "Site"
msgstr "Site"

msgid "Country"
msgstr "Country"

msgid "Description"
msgstr "Description"

# ... etc
```

### 11. Implementation Phases

#### Phase 1: Infrastructure Setup (Week 1)
1. Install Flask-Babel and dependencies
2. Create translation directory structure
3. Configure Flask-Babel in web_interface/app.py
4. Create Desktop GUI i18n module
5. Setup babel.cfg extraction configuration

#### Phase 2: Database Migration (Week 1-2)
1. Create migration script for _it/_en columns
2. Run migration on SQLite test database
3. Verify data integrity
4. Create PostgreSQL migration
5. Add model properties for locale-aware field access

#### Phase 3: Code Refactoring (Week 2-3)
1. Rename service methods (Italian → English)
2. Update variable names in business logic
3. Refactor database manager methods
4. Update API route handlers
5. Run test suite to ensure no regressions

#### Phase 4: Web Interface Translation (Week 3-4)
1. Wrap all template strings with {{ _('...') }}
2. Update WTForms labels with lazy_gettext
3. Add language switcher component
4. Extract strings to .pot file
5. Create Italian and English .po files
6. Compile .mo files

#### Phase 5: Desktop GUI Translation (Week 4)
1. Wrap all menu labels with _()
2. Wrap all dialog strings with _()
3. Add language switcher to preferences
4. Test GUI with both locales

#### Phase 6: API and CLI Translation (Week 5)
1. Add Accept-Language header support
2. Update response schemas for localized fields
3. Update CLI with gettext support
4. Add PYARCHINIT_LANG environment variable

#### Phase 7: GraphML and Export Translation (Week 5)
1. Add locale parameter to GraphML exporter
2. Update node labels based on locale
3. Translate Harris Matrix export labels

#### Phase 8: Testing and Documentation (Week 6)
1. Test all interfaces in IT and EN
2. Test database queries with localized fields
3. Update user documentation
4. Create translation guide for contributors

### 12. Translation Guidelines for Contributors

#### 12.1 Adding New Translatable Strings

**Python code**:
```python
from flask_babel import gettext as _

# Use _() for runtime translation
message = _("Record saved successfully")

# Use lazy_gettext for class-level definitions
from flask_babel import lazy_gettext as _l
label = _l("Save")
```

**Templates**:
```html
<!-- Simple translation -->
<h1>{{ _('Title') }}</h1>

<!-- With variables -->
<p>{{ _('You have %(count)d messages', count=messages|length) }}</p>

<!-- Pluralization -->
<p>{{ ngettext('%(num)d item', '%(num)d items', items|length) }}</p>
```

#### 12.2 Updating Translations

```bash
# 1. Extract new strings
pybabel extract -F pyarchinit_mini/babel.cfg -o pyarchinit_mini/translations/messages.pot .

# 2. Update catalogs
pybabel update -i pyarchinit_mini/translations/messages.pot -d pyarchinit_mini/translations

# 3. Edit .po files manually
# Edit pyarchinit_mini/translations/it/LC_MESSAGES/messages.po
# Edit pyarchinit_mini/translations/en/LC_MESSAGES/messages.po

# 4. Compile
pybabel compile -d pyarchinit_mini/translations
```

### 13. Dependencies to Add

**requirements.txt**:
```txt
Flask-Babel>=3.1.0
Babel>=2.12.0
```

**setup.py**:
```python
install_requires=[
    # ... existing dependencies ...
    'Flask-Babel>=3.1.0',
    'Babel>=2.12.0',
]
```

## Summary

This architecture provides:

✅ **Complete i18n support** for Italian and English across all interfaces
✅ **Database translation** via separate _it/_en columns
✅ **Code refactoring** with English naming conventions
✅ **Professional gettext** implementation for scalability
✅ **Language switcher** in Web UI and Desktop GUI
✅ **API locale support** via Accept-Language header
✅ **GraphML export** with localized labels
✅ **Easy maintenance** with pybabel workflow

The implementation follows industry best practices and is extensible for additional languages in the future.