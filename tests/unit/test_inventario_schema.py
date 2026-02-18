"""Test InventarioMateriali matches pyarchinit schema."""
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali

PYARCHINIT_INVMAT_COLUMNS = [
    'id_invmat', 'sito', 'numero_inventario',
    'tipo_reperto', 'criterio_schedatura', 'definizione', 'descrizione',
    'area', 'us', 'lavato', 'nr_cassa', 'luogo_conservazione',
    'stato_conservazione', 'datazione_reperto', 'elementi_reperto',
    'misurazioni', 'rif_biblio', 'tecnologie',
    'forme_minime', 'forme_massime', 'totale_frammenti',
    'corpo_ceramico', 'rivestimento', 'diametro_orlo', 'peso',
    'tipo', 'eve_orlo', 'repertato', 'diagnostico',
    'n_reperto', 'tipo_contenitore', 'struttura', 'years',
    'schedatore', 'date_scheda', 'punto_rinv', 'negativo_photo', 'diapositiva',
    # Missing from mini-desk:
    'quota_usm', 'unita_misura_quota', 'photo_id', 'drawing_id',
]


def test_inventario_has_all_pyarchinit_columns():
    """InventarioMateriali must have every column from pyarchinit."""
    cols = {c.name for c in InventarioMateriali.__table__.columns}
    missing = [c for c in PYARCHINIT_INVMAT_COLUMNS if c not in cols]
    assert missing == [], f"InventarioMateriali missing: {missing}"
