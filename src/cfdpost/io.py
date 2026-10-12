import numpy as np
import pandas as pd


def read_nodes(path, columns):
    """Liest einen Fluent-CSV-Export. Spaltennamen werden von Leerzeichen befreit.

    columns: dict mit den Schlüsseln x, z, value (Spaltennamen).
    Gibt (x, z, value) als numpy-Arrays zurück.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return (
        df[columns["x"]].values,
        df[columns["z"]].values,
        df[columns["value"]].values,
    )
