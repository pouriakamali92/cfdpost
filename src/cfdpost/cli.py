import argparse

import matplotlib

from .pipeline import compute, load_config, save_table


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cfdpost")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Diagramm und Tabellen aus config.yaml erzeugen")
    run.add_argument("config")
    run.add_argument("--show", action="store_true", help="Diagramm zusätzlich anzeigen")
    args = ap.parse_args(argv)

    if not args.show:
        matplotlib.use("Agg")
    from .plotting import plot_comparison

    cfg = load_config(args.config)
    geom, results = compute(cfg)
    print("Geometrie:", geom)
    for p in save_table(cfg, results):
        print("Tabelle:", p)
    print("Diagramm:", plot_comparison(cfg, results, show=args.show))
