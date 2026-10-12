import numpy as np


def _pick_outer(coord, r, x, z, t, bins):
    """Pro Bin den Punkt mit dem größten Radius wählen (Legacy: kein echtes Mitteln)."""
    ex, ez, et = [], [], []
    for i in range(len(bins) - 1):
        m = (coord >= bins[i]) & (coord < bins[i + 1])
        if m.sum() == 0:
            continue
        idx = np.argmax(r[m])
        ex.append(x[m][idx])
        ez.append(z[m][idx])
        et.append(t[m][idx])
    return np.array(ex), np.array(ez), np.array(et)


def extract_outer_wall(x, z, t, geom, nbins):
    """Außenwand-Pfad (vertikal -> Bogen -> horizontal). Gibt (S, T) zurück.

    S = kumulierte euklidische Distanz zwischen aufeinanderfolgenden Punkten.
    nbins: dict mit den Schlüsseln vertical, bend, horizontal.
    """
    cx, cz, R = geom.cx, geom.cz, geom.R
    theta_min, theta_max = geom.theta_min, geom.theta_max

    # Tangentenpunkte (vertikal nutzt theta_max, horizontal theta_min - wie im Legacy-Code)
    vertical_tangent_z = cz + R * np.cos(theta_max)
    horizontal_tangent_x = cx + R * np.sin(theta_min)

    vertical_mask = z < vertical_tangent_z
    horizontal_mask = x < horizontal_tangent_x
    bend_mask = (~vertical_mask) & (~horizontal_mask)

    # 1. vertikal: Bins in z aufsteigend (fernes Ende -> Bogen)
    xv, zv, tv = x[vertical_mask], z[vertical_mask], t[vertical_mask]
    rv = np.sqrt((zv - cz) ** 2 + (xv - cx) ** 2)
    z_bins = np.linspace(zv.min(), vertical_tangent_z, nbins["vertical"] + 1)
    ex_v, ez_v, et_v = _pick_outer(zv, rv, xv, zv, tv, z_bins)

    # 2. Bogen: Bins im Winkel; danach umdrehen, damit der Pfad vertikal -> horizontal läuft
    xb, zb, tb = x[bend_mask], z[bend_mask], t[bend_mask]
    theta_b = np.arctan2(xb - cx, zb - cz)
    rb = np.sqrt((xb - cx) ** 2 + (zb - cz) ** 2)
    theta_bins = np.linspace(theta_min, theta_max, nbins["bend"] + 1)
    ex_b, ez_b, et_b = _pick_outer(theta_b, rb, xb, zb, tb, theta_bins)
    ex_b, ez_b, et_b = ex_b[::-1], ez_b[::-1], et_b[::-1]

    # 3. horizontal: Bins in x; danach umdrehen (Tangente -> fernes Ende)
    xh, zh, th = x[horizontal_mask], z[horizontal_mask], t[horizontal_mask]
    rh = np.sqrt((xh - cx) ** 2 + (zh - cz) ** 2)
    x_bins = np.linspace(xh.min(), horizontal_tangent_x, nbins["horizontal"] + 1)
    ex_h, ez_h, et_h = _pick_outer(xh, rh, xh, zh, th, x_bins)
    ex_h, ez_h, et_h = ex_h[::-1], ez_h[::-1], et_h[::-1]

    x_all = np.concatenate([ex_v, ex_b, ex_h])
    z_all = np.concatenate([ez_v, ez_b, ez_h])
    T_final = np.concatenate([et_v, et_b, et_h])

    ds = np.sqrt(np.diff(x_all) ** 2 + np.diff(z_all) ** 2)
    S = np.concatenate([[0], np.cumsum(ds)])
    return S, T_final
