from datetime import datetime, timezone
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.pottery_dto import PotteryDTO


def test_dto_round_trip_from_model():
    p = Pottery(
        id_rep=1, id_number=42, sito="X", area="A", us=10, box=2, anno=2024,
        form="Olla", fabric="Coarse", qty=3, diametro_max=15.5,
    )
    dto = PotteryDTO.from_model(p)
    assert dto.id_rep == 1
    assert dto.sito == "X"
    assert dto.form == "Olla"
    assert dto.diametro_max == 15.5
    d = dto.to_dict()
    assert d["sito"] == "X"
    assert d["qty"] == 3


def test_dto_handles_all_qgis_fields():
    qgis_fields = {
        "id_rep", "id_number", "sito", "area", "us", "box", "photo",
        "drawing", "anno", "fabric", "percent", "material", "form",
        "specific_form", "ware", "munsell", "surf_trat", "exdeco",
        "intdeco", "wheel_made", "descrip_ex_deco", "descrip_in_deco",
        "note", "diametro_max", "qty", "diametro_rim", "diametro_bottom",
        "diametro_height", "diametro_preserved", "specific_shape", "bag",
        "sector",
    }
    dto_fields = {f for f in PotteryDTO.__dataclass_fields__.keys()}
    assert qgis_fields.issubset(dto_fields)
