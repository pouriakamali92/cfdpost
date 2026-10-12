import numpy as np


def smooth(y, window=15):
    """Gleitender Mittelwert mit Edge-Padding (Legacy-Verhalten)."""
    pad = window // 2
    y_padded = np.pad(y, pad, mode="edge")
    kernel = np.ones(window) / window
    return np.convolve(y_padded, kernel, mode="valid")
