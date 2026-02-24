"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator

# Base schemas

class BaseSchema(BaseModel):
    """Base schema with common fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Site schemas

class SiteBase(BaseModel):
    """Base site schema"""
    sito: str = Field(..., min_length=1, max_length=350, description="Site name")
    nazione: Optional[str] = Field(None, max_length=250, description="Country")
    regione: Optional[str] = Field(None, max_length=250, description="Region")
    comune: Optional[str] = Field(None, max_length=250, description="Municipality")
    provincia: Optional[str] = Field(None, max_length=10, description="Province")
    definizione_sito: Optional[str] = Field(None, max_length=250, description="Site definition")
    descrizione: Optional[str] = Field(None, description="Description")
    sito_path: Optional[str] = Field(None, max_length=500, description="Site path")
    find_check: Optional[bool] = Field(False, description="Find check flag")

class SiteCreate(SiteBase):
    """Schema for creating a site"""
    pass

class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    sito: Optional[str] = Field(None, min_length=1, max_length=350)
    nazione: Optional[str] = Field(None, max_length=250)
    regione: Optional[str] = Field(None, max_length=250)
    comune: Optional[str] = Field(None, max_length=250)
    provincia: Optional[str] = Field(None, max_length=10)
    definizione_sito: Optional[str] = Field(None, max_length=250)
    descrizione: Optional[str] = None
    sito_path: Optional[str] = Field(None, max_length=500)
    find_check: Optional[bool] = None

class SiteResponse(SiteBase, BaseSchema):
    """Schema for site response"""
    id_sito: int = Field(..., description="Site ID")
    version_number: Optional[int] = None
    entity_uuid: Optional[str] = None
    sync_status: Optional[str] = None

# US (Stratigraphic Unit) schemas

class USBase(BaseModel):
    """Base US schema"""
    sito: str = Field(..., max_length=350, description="Site name")
    area: Optional[str] = Field(None, max_length=20, description="Area")
    us: str = Field(..., description="US number (numeric or alphanumeric, e.g. '1' or 'A1')")

    @validator('us', pre=True)
    def us_to_str(cls, v):
        """Accept int or str — us column is VARCHAR(100)"""
        return str(v).strip() if v is not None else v
    d_stratigrafica: Optional[str] = Field(None, max_length=350, description="Stratigraphic description")
    d_interpretativa: Optional[str] = Field(None, max_length=350, description="Interpretative description")
    descrizione: Optional[str] = Field(None, description="Description")
    interpretazione: Optional[str] = Field(None, description="Interpretation")
    periodo_iniziale: Optional[str] = Field(None, max_length=300, description="Initial period")
    fase_iniziale: Optional[str] = Field(None, max_length=300, description="Initial phase")
    periodo_finale: Optional[str] = Field(None, max_length=300, description="Final period")
    fase_finale: Optional[str] = Field(None, max_length=300, description="Final phase")
    scavato: Optional[str] = Field(None, max_length=20, description="Excavated")
    attivita: Optional[str] = Field(None, max_length=30, description="Activity")
    anno_scavo: Optional[int] = Field(None, ge=1800, le=2100, description="Excavation year")
    metodo_di_scavo: Optional[str] = Field(None, max_length=20, description="Excavation method")
    schedatore: Optional[str] = Field(None, max_length=100, description="Recorder")
    formazione: Optional[str] = Field(None, max_length=20, description="Formation")
    stato_di_conservazione: Optional[str] = Field(None, max_length=20, description="Conservation state")
    colore: Optional[str] = Field(None, max_length=20, description="Color")
    consistenza: Optional[str] = Field(None, max_length=20, description="Consistency")
    struttura: Optional[str] = Field(None, max_length=30, description="Structure")

    # Measurements
    quota_relativa: Optional[float] = Field(None, ge=0, description="Relative elevation")
    quota_abs: Optional[float] = Field(None, ge=0, description="Absolute elevation")
    lunghezza_max: Optional[float] = Field(None, ge=0, description="Maximum length")
    altezza_max: Optional[float] = Field(None, ge=0, description="Maximum height")
    altezza_min: Optional[float] = Field(None, ge=0, description="Minimum height")
    profondita_max: Optional[float] = Field(None, ge=0, description="Maximum depth")
    profondita_min: Optional[float] = Field(None, ge=0, description="Minimum depth")
    larghezza_media: Optional[float] = Field(None, ge=0, description="Average width")

    # Additional fields
    osservazioni: Optional[str] = Field(None, description="Observations")
    datazione: Optional[str] = Field(None, max_length=100, description="Dating")
    direttore_us: Optional[str] = Field(None, max_length=100, description="US director")
    responsabile_us: Optional[str] = Field(None, max_length=100, description="US responsible")

    # i18n fields
    d_stratigrafica_en: Optional[str] = None
    d_interpretativa_en: Optional[str] = None
    descrizione_en: Optional[str] = None
    interpretazione_en: Optional[str] = None
    formazione_en: Optional[str] = None
    stato_di_conservazione_en: Optional[str] = None
    colore_en: Optional[str] = None
    consistenza_en: Optional[str] = None
    struttura_en: Optional[str] = None
    inclusi_en: Optional[str] = None
    campioni_en: Optional[str] = None
    documentazione_en: Optional[str] = None
    osservazioni_en: Optional[str] = None

    # Excavation details
    data_schedatura: Optional[str] = None  # Date as string

    # Documentation and relationships
    inclusi: Optional[str] = None
    campioni: Optional[str] = None
    rapporti: Optional[str] = None
    documentazione: Optional[str] = None
    cont_per: Optional[str] = None
    order_layer: Optional[int] = None

    # USM specific
    unita_tipo: Optional[str] = None
    tipo_documento: Optional[str] = None
    file_path: Optional[str] = None
    settore: Optional[str] = None
    quad_par: Optional[str] = None
    ambient: Optional[str] = None
    saggio: Optional[str] = None

    # USM masonry
    elem_datanti: Optional[str] = None
    funz_statica: Optional[str] = None
    lavorazione: Optional[str] = None
    spess_giunti: Optional[str] = None
    letti_posa: Optional[str] = None
    alt_mod: Optional[str] = None
    un_ed_riass: Optional[str] = None
    reimp: Optional[str] = None
    posa_opera: Optional[str] = None
    quota_min_usm: Optional[float] = None
    quota_max_usm: Optional[float] = None
    cons_legante: Optional[str] = None
    col_legante: Optional[str] = None
    aggreg_legante: Optional[str] = None
    con_text_mat: Optional[str] = None
    col_materiale: Optional[str] = None
    inclusi_materiali_usm: Optional[str] = None

    # ICCD
    n_catalogo_generale: Optional[str] = None
    n_catalogo_interno: Optional[str] = None
    n_catalogo_internazionale: Optional[str] = None
    soprintendenza: Optional[str] = None

    # References and position
    ref_tm: Optional[str] = None
    ref_ra: Optional[str] = None
    ref_n: Optional[str] = None
    posizione: Optional[str] = None
    criteri_distinzione: Optional[str] = None
    modo_formazione: Optional[str] = None
    componenti_organici: Optional[str] = None
    componenti_inorganici: Optional[str] = None

    # Extended quota measurements
    quota_max_abs: Optional[float] = None
    quota_max_rel: Optional[float] = None
    quota_min_abs: Optional[float] = None
    quota_min_rel: Optional[float] = None

    # Additional data
    flottazione: Optional[str] = None
    setacciatura: Optional[str] = None
    affidabilita: Optional[str] = None

    # Administrative
    cod_ente_schedatore: Optional[str] = None
    data_rilevazione: Optional[str] = None
    data_rielaborazione: Optional[str] = None

    # USM extended
    lunghezza_usm: Optional[float] = None
    altezza_usm: Optional[float] = None
    spessore_usm: Optional[float] = None
    tecnica_muraria_usm: Optional[str] = None
    modulo_usm: Optional[str] = None
    campioni_malta_usm: Optional[str] = None
    campioni_mattone_usm: Optional[str] = None
    campioni_pietra_usm: Optional[str] = None
    provenienza_materiali_usm: Optional[str] = None
    criteri_distinzione_usm: Optional[str] = None
    uso_primario_usm: Optional[str] = None
    tipologia_opera: Optional[str] = None
    sezione_muraria: Optional[str] = None
    superficie_analizzata: Optional[str] = None
    orientamento: Optional[str] = None

    # Laterizio
    materiali_lat: Optional[str] = None
    lavorazione_lat: Optional[str] = None
    consistenza_lat: Optional[str] = None
    forma_lat: Optional[str] = None
    colore_lat: Optional[str] = None
    impasto_lat: Optional[str] = None

    # Pietra
    forma_p: Optional[str] = None
    colore_p: Optional[str] = None
    taglio_p: Optional[str] = None
    posa_opera_p: Optional[str] = None

    # Other USM
    inerti_usm: Optional[str] = None
    tipo_legante_usm: Optional[str] = None
    rifinitura_usm: Optional[str] = None
    materiale_p: Optional[str] = None
    consistenza_p: Optional[str] = None

    # Extended relationships
    rapporti2: Optional[str] = None
    doc_usv: Optional[str] = None

class USCreate(USBase):
    """Schema for creating a US"""
    pass

class USUpdate(BaseModel):
    """Schema for updating a US"""
    sito: Optional[str] = Field(None, max_length=350)
    area: Optional[str] = Field(None, max_length=20)
    us: Optional[str] = Field(None, description="US number (numeric or alphanumeric)")

    @validator('us', pre=True)
    def us_to_str(cls, v):
        return str(v).strip() if v is not None else v
    d_stratigrafica: Optional[str] = Field(None, max_length=350)
    d_interpretativa: Optional[str] = Field(None, max_length=350)
    descrizione: Optional[str] = None
    interpretazione: Optional[str] = None
    periodo_iniziale: Optional[str] = Field(None, max_length=300)
    fase_iniziale: Optional[str] = Field(None, max_length=300)
    periodo_finale: Optional[str] = Field(None, max_length=300)
    fase_finale: Optional[str] = Field(None, max_length=300)
    scavato: Optional[str] = Field(None, max_length=20)
    attivita: Optional[str] = Field(None, max_length=30)
    anno_scavo: Optional[int] = Field(None, ge=1800, le=2100)
    metodo_di_scavo: Optional[str] = Field(None, max_length=20)
    schedatore: Optional[str] = Field(None, max_length=100)
    formazione: Optional[str] = Field(None, max_length=20)
    stato_di_conservazione: Optional[str] = Field(None, max_length=20)
    colore: Optional[str] = Field(None, max_length=20)
    consistenza: Optional[str] = Field(None, max_length=20)
    struttura: Optional[str] = Field(None, max_length=30)

    # Measurements
    quota_relativa: Optional[float] = None
    quota_abs: Optional[float] = None
    lunghezza_max: Optional[float] = None
    altezza_max: Optional[float] = None
    altezza_min: Optional[float] = None
    profondita_max: Optional[float] = None
    profondita_min: Optional[float] = None
    larghezza_media: Optional[float] = None

    # Additional fields
    osservazioni: Optional[str] = None
    datazione: Optional[str] = Field(None, max_length=100)
    direttore_us: Optional[str] = Field(None, max_length=100)
    responsabile_us: Optional[str] = Field(None, max_length=100)

    # i18n fields
    d_stratigrafica_en: Optional[str] = None
    d_interpretativa_en: Optional[str] = None
    descrizione_en: Optional[str] = None
    interpretazione_en: Optional[str] = None
    formazione_en: Optional[str] = None
    stato_di_conservazione_en: Optional[str] = None
    colore_en: Optional[str] = None
    consistenza_en: Optional[str] = None
    struttura_en: Optional[str] = None
    inclusi_en: Optional[str] = None
    campioni_en: Optional[str] = None
    documentazione_en: Optional[str] = None
    osservazioni_en: Optional[str] = None

    # Excavation details
    data_schedatura: Optional[str] = None

    # Documentation and relationships
    inclusi: Optional[str] = None
    campioni: Optional[str] = None
    rapporti: Optional[str] = None
    documentazione: Optional[str] = None
    cont_per: Optional[str] = None
    order_layer: Optional[int] = None

    # USM specific
    unita_tipo: Optional[str] = None
    tipo_documento: Optional[str] = None
    file_path: Optional[str] = None
    settore: Optional[str] = None
    quad_par: Optional[str] = None
    ambient: Optional[str] = None
    saggio: Optional[str] = None

    # USM masonry
    elem_datanti: Optional[str] = None
    funz_statica: Optional[str] = None
    lavorazione: Optional[str] = None
    spess_giunti: Optional[str] = None
    letti_posa: Optional[str] = None
    alt_mod: Optional[str] = None
    un_ed_riass: Optional[str] = None
    reimp: Optional[str] = None
    posa_opera: Optional[str] = None
    quota_min_usm: Optional[float] = None
    quota_max_usm: Optional[float] = None
    cons_legante: Optional[str] = None
    col_legante: Optional[str] = None
    aggreg_legante: Optional[str] = None
    con_text_mat: Optional[str] = None
    col_materiale: Optional[str] = None
    inclusi_materiali_usm: Optional[str] = None

    # ICCD
    n_catalogo_generale: Optional[str] = None
    n_catalogo_interno: Optional[str] = None
    n_catalogo_internazionale: Optional[str] = None
    soprintendenza: Optional[str] = None

    # References and position
    ref_tm: Optional[str] = None
    ref_ra: Optional[str] = None
    ref_n: Optional[str] = None
    posizione: Optional[str] = None
    criteri_distinzione: Optional[str] = None
    modo_formazione: Optional[str] = None
    componenti_organici: Optional[str] = None
    componenti_inorganici: Optional[str] = None

    # Extended quota measurements
    quota_max_abs: Optional[float] = None
    quota_max_rel: Optional[float] = None
    quota_min_abs: Optional[float] = None
    quota_min_rel: Optional[float] = None

    # Additional data
    flottazione: Optional[str] = None
    setacciatura: Optional[str] = None
    affidabilita: Optional[str] = None

    # Administrative
    cod_ente_schedatore: Optional[str] = None
    data_rilevazione: Optional[str] = None
    data_rielaborazione: Optional[str] = None

    # USM extended
    lunghezza_usm: Optional[float] = None
    altezza_usm: Optional[float] = None
    spessore_usm: Optional[float] = None
    tecnica_muraria_usm: Optional[str] = None
    modulo_usm: Optional[str] = None
    campioni_malta_usm: Optional[str] = None
    campioni_mattone_usm: Optional[str] = None
    campioni_pietra_usm: Optional[str] = None
    provenienza_materiali_usm: Optional[str] = None
    criteri_distinzione_usm: Optional[str] = None
    uso_primario_usm: Optional[str] = None
    tipologia_opera: Optional[str] = None
    sezione_muraria: Optional[str] = None
    superficie_analizzata: Optional[str] = None
    orientamento: Optional[str] = None

    # Laterizio
    materiali_lat: Optional[str] = None
    lavorazione_lat: Optional[str] = None
    consistenza_lat: Optional[str] = None
    forma_lat: Optional[str] = None
    colore_lat: Optional[str] = None
    impasto_lat: Optional[str] = None

    # Pietra
    forma_p: Optional[str] = None
    colore_p: Optional[str] = None
    taglio_p: Optional[str] = None
    posa_opera_p: Optional[str] = None

    # Other USM
    inerti_usm: Optional[str] = None
    tipo_legante_usm: Optional[str] = None
    rifinitura_usm: Optional[str] = None
    materiale_p: Optional[str] = None
    consistenza_p: Optional[str] = None

    # Extended relationships
    rapporti2: Optional[str] = None
    doc_usv: Optional[str] = None

class USResponse(USBase, BaseSchema):
    """Schema for US response"""
    id_us: int = Field(..., description="US ID")
    version_number: Optional[int] = None
    entity_uuid: Optional[str] = None
    sync_status: Optional[str] = None

# Inventario Materiali schemas

class InventarioBase(BaseModel):
    """Base inventory schema"""
    sito: str = Field(..., max_length=350, description="Site name")
    numero_inventario: int = Field(..., gt=0, description="Inventory number")
    tipo_reperto: Optional[str] = Field(None, max_length=20, description="Find type")
    criterio_schedatura: Optional[str] = Field(None, max_length=20, description="Recording criteria")
    definizione: Optional[str] = Field(None, max_length=20, description="Definition")
    descrizione: Optional[str] = Field(None, description="Description")
    area: Optional[str] = Field(None, max_length=20, description="Area")
    us: Optional[str] = Field(None, description="US number (numeric or alphanumeric)")
    lavato: Optional[str] = Field(None, max_length=5, description="Washed")
    nr_cassa: Optional[str] = Field(None, max_length=20, description="Box number")
    luogo_conservazione: Optional[str] = Field(None, max_length=350, description="Conservation location")
    stato_conservazione: Optional[str] = Field(None, max_length=200, description="Conservation state")
    datazione_reperto: Optional[str] = Field(None, max_length=100, description="Find dating")

    # Technical characteristics
    forme_minime: Optional[int] = Field(None, ge=0, description="Minimum forms")
    forme_massime: Optional[int] = Field(None, ge=0, description="Maximum forms")
    totale_frammenti: Optional[int] = Field(None, ge=0, description="Total fragments")
    peso: Optional[float] = Field(None, ge=0, description="Weight")
    diametro_orlo: Optional[float] = Field(None, ge=0, description="Rim diameter")
    eve_orlo: Optional[float] = Field(None, ge=0, le=100, description="Rim EVE")

    # Classification
    corpo_ceramico: Optional[str] = Field(None, max_length=20, description="Ceramic body")
    rivestimento: Optional[str] = Field(None, max_length=20, description="Surface treatment")
    tipo: Optional[str] = Field(None, max_length=300, description="Type")
    repertato: Optional[str] = Field(None, max_length=2, description="Catalogued")
    diagnostico: Optional[str] = Field(None, max_length=2, description="Diagnostic")

    # Additional fields from pyarchinit
    quota_usm: Optional[float] = None
    unita_misura_quota: Optional[str] = None
    photo_id: Optional[str] = None
    drawing_id: Optional[str] = None

    @validator('lavato', 'repertato', 'diagnostico')
    def validate_yes_no_fields(cls, v):
        if v is not None and v.upper() not in ['SI', 'NO', 'S', 'N']:
            raise ValueError('Must be SI/NO or S/N')
        return v

class InventarioCreate(InventarioBase):
    """Schema for creating inventory item"""
    pass

class InventarioUpdate(BaseModel):
    """Schema for updating inventory item"""
    sito: Optional[str] = Field(None, max_length=350)
    numero_inventario: Optional[int] = Field(None, gt=0)
    tipo_reperto: Optional[str] = Field(None, max_length=20)
    criterio_schedatura: Optional[str] = Field(None, max_length=20)
    definizione: Optional[str] = Field(None, max_length=20)
    descrizione: Optional[str] = None
    area: Optional[str] = Field(None, max_length=20)
    us: Optional[str] = Field(None, description="US number")
    lavato: Optional[str] = Field(None, max_length=5)
    nr_cassa: Optional[str] = Field(None, max_length=20)
    luogo_conservazione: Optional[str] = Field(None, max_length=350)
    stato_conservazione: Optional[str] = Field(None, max_length=200)
    datazione_reperto: Optional[str] = Field(None, max_length=100)
    forme_minime: Optional[int] = None
    forme_massime: Optional[int] = None
    totale_frammenti: Optional[int] = None
    peso: Optional[float] = None
    diametro_orlo: Optional[float] = None
    eve_orlo: Optional[float] = None
    corpo_ceramico: Optional[str] = Field(None, max_length=20)
    rivestimento: Optional[str] = Field(None, max_length=20)
    tipo: Optional[str] = Field(None, max_length=300)
    repertato: Optional[str] = Field(None, max_length=2)
    diagnostico: Optional[str] = Field(None, max_length=2)

    # Additional fields from pyarchinit
    quota_usm: Optional[float] = None
    unita_misura_quota: Optional[str] = None
    photo_id: Optional[str] = None
    drawing_id: Optional[str] = None

class InventarioResponse(InventarioBase, BaseSchema):
    """Schema for inventory response"""
    id_invmat: int = Field(..., description="Inventory ID")
    version_number: Optional[int] = None
    entity_uuid: Optional[str] = None
    sync_status: Optional[str] = None

# Pagination schemas

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[BaseModel]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        from_attributes = True
