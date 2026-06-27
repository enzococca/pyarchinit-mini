import json, pytest
from pyarchinit_mini.sync.config import load_config, Config, DEFAULT_PRESERVE

def test_load_config_resolves_dsn_from_env(tmp_path):
    cfg_file = tmp_path / "c.json"
    cfg_file.write_text(json.dumps({
        "source_dsn_env": "SRC", "target_dsn_env": "TGT",
        "size_threshold_keyset": 50,
        "overrides": {"shape_finali_polygon": {"mode": "replace"}},
    }))
    env = {"SRC": "postgresql://x@h/classic", "TGT": "postgresql://x@h/v2"}
    cfg = load_config(str(cfg_file), env=env)
    assert cfg.source_dsn == "postgresql://x@h/classic"
    assert cfg.target_dsn == "postgresql://x@h/v2"
    assert cfg.size_threshold_keyset == 50
    assert cfg.overrides["shape_finali_polygon"]["mode"] == "replace"
    assert "order_layer" in cfg.preserve_columns_global
    assert cfg.delete_enabled is True

def test_load_config_missing_env_raises():
    with pytest.raises(KeyError):
        load_config(None, env={})

def test_collision_id_base_default_and_override(tmp_path):
    import json
    from pyarchinit_mini.sync.config import load_config
    env = {"SRC": "postgresql://x@h/c", "TGT": "postgresql://x@h/v2"}
    cfg = load_config(None, env={**env, "PYARCHINIT_CLASSIC_DSN": env["SRC"], "DATABASE_URL": env["TGT"]})
    assert cfg.collision_id_base == 1_000_000_000
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"source_dsn_env": "SRC", "target_dsn_env": "TGT", "collision_id_base": 5000}))
    cfg2 = load_config(str(f), env=env)
    assert cfg2.collision_id_base == 5000
