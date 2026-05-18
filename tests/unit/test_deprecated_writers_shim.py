import warnings
import importlib
import pytest


@pytest.mark.parametrize("module_name", [
    "pyarchinit_mini.graphml_converter.graphml_builder",
    "pyarchinit_mini.graphml_converter.graphml_exporter",
    "pyarchinit_mini.graphml_converter.pure_networkx_exporter",
    "pyarchinit_mini.graphml_converter.converter",
])
def test_legacy_writer_module_emits_deprecation_warning(module_name):
    # Force re-import so module-level warning fires
    if module_name in list(globals()):
        pass  # not needed; just trying reload semantics
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        # Re-import (reload) the module to trigger the module-level warning
        try:
            mod = importlib.import_module(module_name)
            importlib.reload(mod)
        except Exception as e:
            pytest.fail(f"Module import/reload failed: {e}")
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("deprecated" in str(w.message).lower() for w in deprecations), \
        f"Expected DeprecationWarning from {module_name}; got: {[str(w.message) for w in caught]}"
