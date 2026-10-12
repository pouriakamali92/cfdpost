from pathlib import Path

import numpy as np
import yaml

from .geometry import fit_bend_geometry
from .io import read_nodes
from .smoothing import smooth
from .wall import extract_outer_wall


def load_config(path):
    path = Path(path).resolve()
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_base"] = path.parent
    return cfg


def _resolve(cfg, p):
    p = Path(p)
    return p if p.is_absolute() else cfg["_base"] / p


def compute(cfg):
    """Führt die Berechnung aus. Gibt (geometry, results) zurück.

    results: dict name -> dict(S, T, T_smooth)
    """
    cols = cfg["columns"]
    versions = cfg["versions"]
    ref_name = cfg["geometry"]["reference"]
    ref = next(v for v in versions if v["name"] == ref_name)

    x, z, _ = read_nodes(_resolve(cfg, ref["file"]), cols)
    geom = fit_bend_geometry(x, z, cfg["geometry"]["bend_mask"], cfg["geometry"]["fit_bins"])

    results = {}
    for v in versions:
        x, z, t = read_nodes(_resolve(cfg, v["file"]), cols)
        S, T = extract_outer_wall(x, z, t, geom, cfg["wall"]["bins"])
        results[v["name"]] = {"S": S, "T": T, "T_smooth": smooth(T, cfg["smoothing"]["window"])}
    return geom, results


def save_table(cfg, results):
    """Zahlentabelle: je Version eine CSV mit S, T, T_smooth."""
    out_dir = _resolve(cfg, cfg["output"]["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, r in results.items():
        p = out_dir / f"{name}_wand.csv"
        data = np.column_stack([r["S"], r["T"], r["T_smooth"]])
        np.savetxt(p, data, delimiter=",", header="S_m,T_raw_K,T_smooth_K", comments="")
        paths.append(p)
    return paths
