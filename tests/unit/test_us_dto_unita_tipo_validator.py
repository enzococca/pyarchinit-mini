import warnings
from pathlib import Path
import pytest

from pyarchinit_mini.dto.us_dto import USDTO
from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_known_unit_type_accepted_silently():
    d = USDTO(id_us=1, sito="S", us=1, unita_tipo="US")
    # Should not raise, should not warn
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        d.validate_unita_tipo()
        assert not any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_legacy_usva_accepted_with_deprecation_warning():
    d = USDTO(id_us=1, sito="S", us=1, unita_tipo="USVA")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        d.validate_unita_tipo()
        deprecation_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(deprecation_warnings) >= 1
        msg = str(deprecation_warnings[0].message)
        assert "USVA" in msg
        assert "USVs" in msg  # suggested replacement


def test_legacy_usvc_suggests_usvn():
    d = USDTO(id_us=1, sito="S", us=1, unita_tipo="USVC")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        d.validate_unita_tipo()
        deprecation_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert any("USVn" in str(w.message) for w in deprecation_warnings)


def test_unknown_unit_type_raises_value_error():
    d = USDTO(id_us=1, sito="S", us=1, unita_tipo="ZZZ_UNKNOWN_TYPE")
    with pytest.raises(ValueError) as exc_info:
        d.validate_unita_tipo()
    msg = str(exc_info.value).lower()
    assert "unknown" in msg or "zzz_unknown_type" in msg


def test_empty_unita_tipo_passes_silently():
    """Empty unita_tipo is allowed (column is nullable in legacy data); skip validation."""
    d = USDTO(id_us=1, sito="S", us=1, unita_tipo=None)
    d.validate_unita_tipo()  # no raise
    d2 = USDTO(id_us=2, sito="S", us=1, unita_tipo="")
    d2.validate_unita_tipo()  # no raise
