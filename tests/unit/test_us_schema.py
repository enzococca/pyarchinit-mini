"""Test that US model matches pyarchinit us_table schema exactly."""
from pyarchinit_mini.models.us import US

# All columns from pyarchinit US_table.py (canonical source)
PYARCHINIT_US_COLUMNS = [
    'id_us', 'sito', 'area', 'us',
    'd_stratigrafica', 'd_interpretativa', 'descrizione', 'interpretazione',
    'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
    'scavato', 'attivita', 'anno_scavo', 'metodo_di_scavo',
    'inclusi', 'campioni', 'rapporti', 'data_schedatura', 'schedatore',
    'formazione', 'stato_di_conservazione', 'colore', 'consistenza', 'struttura',
    'cont_per', 'order_layer', 'documentazione',
    'unita_tipo', 'settore', 'quad_par', 'ambient', 'saggio',
    'elem_datanti', 'funz_statica', 'lavorazione', 'spess_giunti',
    'letti_posa', 'alt_mod', 'un_ed_riass', 'reimp', 'posa_opera',
    'quota_min_usm', 'quota_max_usm',
    'cons_legante', 'col_legante', 'aggreg_legante',
    'con_text_mat', 'col_materiale', 'inclusi_materiali_usm',
    'n_catalogo_generale', 'n_catalogo_interno', 'n_catalogo_internazionale',
    'soprintendenza',
    'quota_relativa', 'quota_abs',
    'ref_tm', 'ref_ra', 'ref_n', 'posizione',
    'criteri_distinzione', 'modo_formazione',
    'componenti_organici', 'componenti_inorganici',
    'lunghezza_max', 'altezza_max', 'altezza_min',
    'profondita_max', 'profondita_min', 'larghezza_media',
    'quota_max_abs', 'quota_max_rel', 'quota_min_abs', 'quota_min_rel',
    'osservazioni', 'datazione', 'flottazione', 'setacciatura',
    'affidabilita', 'direttore_us', 'responsabile_us',
    'cod_ente_schedatore', 'data_rilevazione', 'data_rielaborazione',
    'lunghezza_usm', 'altezza_usm', 'spessore_usm',
    'tecnica_muraria_usm', 'modulo_usm',
    'campioni_malta_usm', 'campioni_mattone_usm', 'campioni_pietra_usm',
    'provenienza_materiali_usm', 'criteri_distinzione_usm', 'uso_primario_usm',
    'tipologia_opera', 'sezione_muraria', 'superficie_analizzata', 'orientamento',
    'materiali_lat', 'lavorazione_lat', 'consistenza_lat',
    'forma_lat', 'colore_lat', 'impasto_lat',
    'forma_p', 'colore_p', 'taglio_p', 'posa_opera_p',
    'inerti_usm', 'tipo_legante_usm', 'rifinitura_usm',
    'materiale_p', 'consistenza_p',
    'rapporti2', 'doc_usv',
    'tipo_documento', 'file_path',
]


def test_us_has_all_pyarchinit_columns():
    """US model must have every column from pyarchinit US_table.py."""
    us_columns = {c.name for c in US.__table__.columns}
    missing = [col for col in PYARCHINIT_US_COLUMNS if col not in us_columns]
    assert missing == [], f"US model missing columns: {missing}"
