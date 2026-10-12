from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Geometry:
    cx: float
    cz: float
    R: float
    theta_min: float
    theta_max: float


def _fit_circle(x, z):
    """Kreis-Fit (kleinste Quadrate): x^2+z^2 = 2*cx*x + 2*cz*z + c."""
    A = np.column_stack([x, z, np.ones_like(x)])
    b = (x**2) + (z**2)
    result, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx = result[0] / 2
    cz = result[1] / 2
    R = np.sqrt(result[2] + cx**2 + cz**2)
    return cx, cz, R


def fit_bend_geometry(x, z, mask_cfg, nbins):
    """Bestimmt Mittelpunkt, Radius und Winkelbereich des Krümmers (Legacy-Algorithmus)."""
    bend_mask = (
        (x > mask_cfg["x_min"]) & (x < mask_cfg["x_max"])
        & (z > mask_cfg["z_min"]) & (z < mask_cfg["z_max"])
    )
    x_bend = x[bend_mask]
    z_bend = z[bend_mask]

    cx, cz, R = _fit_circle(x_bend, z_bend)

    theta = np.arctan2(x_bend - cx, z_bend - cz)
    r = np.sqrt((x_bend - cx) ** 2 + (z_bend - cz) ** 2)

    bins = np.linspace(theta.min(), theta.max(), nbins + 1)
    extrados_x = []
    extrados_z = []
    for i in range(nbins):
        m = (theta >= bins[i]) & (theta < bins[i + 1])
        if m.sum() == 0:
            continue
        idx = np.argmax(r[m])
        extrados_x.append(x_bend[m][idx])
        extrados_z.append(z_bend[m][idx])
    extrados_x = np.array(extrados_x)
    extrados_z = np.array(extrados_z)

    cx, cz, R = _fit_circle(extrados_x, extrados_z)

    theta_final = np.arctan2(extrados_x - cx, extrados_z - cz)
    return Geometry(cx, cz, R, theta_final.min(), theta_final.max())
