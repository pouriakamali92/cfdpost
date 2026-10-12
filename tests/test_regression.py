"""Regressionstest: neuer Code muss das Legacy-Ergebnis numerisch reproduzieren."""
from pathlib import Path

import numpy as np
import pytest

from cfdpost.pipeline import compute, load_config

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "golden.npz"


@pytest.fixture(scope="module")
def new_results():
    cfg = load_config(ROOT / "config.yaml")
    for v in cfg["versions"]:
        if not (ROOT / v["file"]).exists():
            pytest.skip(f"Datendatei fehlt: {v['file']}")
    return compute(cfg)


@pytest.fixture(scope="module")
def golden():
    if not GOLDEN.exists():
        pytest.skip("Referenzdaten (tests/golden/golden.npz) sind nicht im Repository enthalten")
    return np.load(GOLDEN)


def test_geometry(new_results, golden):
    geom, _ = new_results
    for k in ("cx", "cz", "R", "theta_min", "theta_max"):
        assert np.allclose(getattr(geom, k), golden[f"geom_{k}"], rtol=1e-12, atol=0), k


@pytest.mark.parametrize("name", ["v1", "v2", "v3", "v4"])
def test_version(name, new_results, golden):
    _, results = new_results
    r = results[name]
    for key, gkey in (("S", "S"), ("T", "T"), ("T_smooth", "T_smooth")):
        ref = golden[f"{name}_{gkey}"]
        assert r[key].shape == ref.shape, f"{name} {key}: andere Länge"
        assert np.allclose(r[key], ref, rtol=1e-12, atol=0), f"{name} {key}: Abweichung"
