import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- 1. Read the reference file and prepare arrays ----------
dataframe_1 = pd.read_csv('v1.h5')
dataframe_1.columns = [c.strip() for c in dataframe_1.columns]
X = dataframe_1['x-coordinate'].values
Z = dataframe_1['z-coordinate'].values
T = dataframe_1['total-temperature'].values


# ---------- 2. Fit the bend geometry (center, radius, angular range) ----------
def fit_bend_geometry(x, z):
    bend_mask = (x > -0.5) & (x < 0.15) & (z > 0.72) & (z < 1.05)
    x_bend = x[bend_mask]
    z_bend = z[bend_mask]

    A = np.column_stack([x_bend, z_bend, np.ones_like(x_bend)])
    b = (x_bend**2) + (z_bend**2)
    result, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx = result[0] / 2
    cz = result[1] / 2
    R = np.sqrt(result[2] + cx**2 + cz**2)

    theta = np.arctan2(x_bend - cx, z_bend - cz)
    r = np.sqrt((x_bend - cx)**2 + (z_bend - cz)**2)

    nbins = 60
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

    A2 = np.column_stack([extrados_x, extrados_z, np.ones_like(extrados_x)])
    b2 = (extrados_x**2) + (extrados_z**2)
    result2, *_ = np.linalg.lstsq(A2, b2, rcond=None)
    cx = result2[0] / 2
    cz = result2[1] / 2
    R = np.sqrt(result2[2] + cx**2 + cz**2)

    theta_final = np.arctan2(extrados_x - cx, extrados_z - cz)
    theta_min = theta_final.min()
    theta_max = theta_final.max()
    return cx, cz, R, theta_min, theta_max


cx, cz, R, theta_min, theta_max = fit_bend_geometry(X, Z)
print("cx", cx, "cz", cz, "R", R, "theta_min", theta_min, "theta_max", theta_max)


# ---------- 3. Extract the outer-wall path (vertical + bend + horizontal) ----------
# Distance along the path (S) is built from the real Euclidean distance between
# consecutive extracted points, instead of separate per-section formulas -- this
# guarantees a continuous path with no jump at the section boundaries, regardless
# of how accurate the fitted radius R is.
def extract_outer_wall(filename, geom):
    cx, cz, R, theta_min, theta_max = geom
    dataframe_2 = pd.read_csv(filename)
    dataframe_2.columns = [c.strip() for c in dataframe_2.columns]
    x = dataframe_2['x-coordinate'].values
    z = dataframe_2['z-coordinate'].values
    t = dataframe_2['total-temperature'].values

    # tangent points (vertical uses theta_max, horizontal uses theta_min --
    # matches the actual angular convention found for this geometry)
    vertical_tangent_z = cz + R * np.cos(theta_max)
    horizontal_tangent_x = cx + R * np.sin(theta_min)

    vertical_mask = z < vertical_tangent_z
    horizontal_mask = x < horizontal_tangent_x
    bend_mask = (~vertical_mask) & (~horizontal_mask)

    # --- 1. vertical side: binned by z, ascending (far end -> bend) ---
    x_vertical = x[vertical_mask]
    z_vertical = z[vertical_mask]
    t_vertical = t[vertical_mask]
    nbins = 40
    z_bins = np.linspace(z_vertical.min(), vertical_tangent_z, nbins + 1)
    r_vertical = np.sqrt((z_vertical - cz)**2 + (x_vertical - cx)**2)
    ex_vertical, ez_vertical, et_vertical = [], [], []
    for i in range(nbins):
        V = (z_vertical >= z_bins[i]) & (z_vertical < z_bins[i + 1])
        if V.sum() == 0:
            continue
        idx = np.argmax(r_vertical[V])
        ex_vertical.append(x_vertical[V][idx])
        ez_vertical.append(z_vertical[V][idx])
        et_vertical.append(t_vertical[V][idx])
    ex_vertical = np.array(ex_vertical)
    ez_vertical = np.array(ez_vertical)
    et_vertical = np.array(et_vertical)

    # --- 2. arc (bend) side: binned by theta ---
    x_bend = x[bend_mask]
    z_bend = z[bend_mask]
    t_bend = t[bend_mask]
    theta_bend = np.arctan2(x_bend - cx, z_bend - cz)
    r_bend = np.sqrt((x_bend - cx)**2 + (z_bend - cz)**2)
    nbins_bend = 60
    theta_bins = np.linspace(theta_min, theta_max, nbins_bend + 1)
    ex_bend, ez_bend, et_bend = [], [], []
    for i in range(nbins_bend):
        J = (theta_bend >= theta_bins[i]) & (theta_bend < theta_bins[i + 1])
        if J.sum() == 0:
            continue
        idx = np.argmax(r_bend[J])
        ex_bend.append(x_bend[J][idx])
        ez_bend.append(z_bend[J][idx])
        et_bend.append(t_bend[J][idx])
    ex_bend = np.array(ex_bend)
    ez_bend = np.array(ez_bend)
    et_bend = np.array(et_bend)
    # theta_max corresponds to the vertical-side tangent, theta_min to the
    # horizontal-side tangent -- reverse so the array runs vertical -> horizontal
    ex_bend, ez_bend, et_bend = ex_bend[::-1], ez_bend[::-1], et_bend[::-1]

    # --- 3. horizontal side: binned by x ---
    x_horizontal = x[horizontal_mask]
    z_horizontal = z[horizontal_mask]
    t_horizontal = t[horizontal_mask]
    r_horizontal = np.sqrt((x_horizontal - cx)**2 + (z_horizontal - cz)**2)
    nbins_horizontal = 40
    x_bins = np.linspace(x_horizontal.min(), horizontal_tangent_x, nbins_horizontal + 1)
    ex_horizontal, ez_horizontal, et_horizontal = [], [], []
    for i in range(nbins_horizontal):
        H = (x_horizontal >= x_bins[i]) & (x_horizontal < x_bins[i + 1])
        if H.sum() == 0:
            continue
        idx = np.argmax(r_horizontal[H])
        ex_horizontal.append(x_horizontal[H][idx])
        ez_horizontal.append(z_horizontal[H][idx])
        et_horizontal.append(t_horizontal[H][idx])
    ex_horizontal = np.array(ex_horizontal)
    ez_horizontal = np.array(ez_horizontal)
    et_horizontal = np.array(et_horizontal)
    # loop went far-end -> tangent; reverse so it continues tangent -> far-end
    ex_horizontal, ez_horizontal, et_horizontal = ex_horizontal[::-1], ez_horizontal[::-1], et_horizontal[::-1]

    # --- combine all three sections in physical order and build S from real distances ---
    x_all = np.concatenate([ex_vertical, ex_bend, ex_horizontal])
    z_all = np.concatenate([ez_vertical, ez_bend, ez_horizontal])
    T_final = np.concatenate([et_vertical, et_bend, et_horizontal])

    ds = np.sqrt(np.diff(x_all)**2 + np.diff(z_all)**2)
    S = np.concatenate([[0], np.cumsum(ds)])
    return S, T_final


# ---------- 4. Smoothing helper (moving average, edge-padded) ----------
def smooth(y, window=15):
    pad = window // 2
    y_padded = np.pad(y, pad, mode='edge')
    kernel = np.ones(window) / window
    return np.convolve(y_padded, kernel, mode='valid')


# ---------- 5. Run for all four files ----------
my_geometry = (cx, cz, R, theta_min, theta_max)
S_V1, T_V1 = extract_outer_wall('v1.h5', my_geometry)
S_V2, T_V2 = extract_outer_wall('v2', my_geometry)
S_V3, T_V3 = extract_outer_wall('v3', my_geometry)
S_V4, T_V4 = extract_outer_wall('v4', my_geometry)

T_V1_smooth = smooth(T_V1, window=15)
T_V2_smooth = smooth(T_V2, window=15)
T_V3_smooth = smooth(T_V3, window=15)
T_V4_smooth = smooth(T_V4, window=15)

# ---------- 6. Plot ----------
plt.figure(figsize=(12, 8))
plt.plot(S_V1, T_V1_smooth, label='Version1', color='red', linewidth=2)
plt.plot(S_V2, T_V2_smooth, label='Version2', color='gold', linewidth=2)
plt.plot(S_V3, T_V3_smooth, label='Version3', color='green', linewidth=2)
plt.plot(S_V4, T_V4_smooth, label='Version4', color='blue', linewidth=2)
plt.xlabel('Distance along outer wall S (m)')
plt.ylabel('Temperature (K)')
plt.title('gemittelte Temperatur auf der innenseite der Außenwand')
plt.legend()
plt.grid(True)
plt.savefig('gemittelte_Temperatur_smoothed.png', dpi=200, facecolor='white')
plt.show()
