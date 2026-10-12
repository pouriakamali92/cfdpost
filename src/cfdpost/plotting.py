import matplotlib.pyplot as plt

from .pipeline import _resolve


def plot_comparison(cfg, results, show=False):
    pc = cfg["plot"]
    plt.figure(figsize=tuple(pc["figsize"]))
    for v in cfg["versions"]:
        r = results[v["name"]]
        plt.plot(r["S"], r["T_smooth"], label=v["label"], color=v["color"], linewidth=pc["linewidth"])
    plt.xlabel(pc["xlabel"])
    plt.ylabel(pc["ylabel"])
    plt.title(pc["title"])
    plt.legend()
    plt.grid(True)
    out_dir = _resolve(cfg, cfg["output"]["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / pc["filename"]
    plt.savefig(out, dpi=pc["dpi"], facecolor="white")
    if show:
        plt.show()
    plt.close()
    return out
