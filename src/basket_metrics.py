"""Tools to audit basket-value data and compute a robust average."""

import numpy as np
import pandas as pd
from scipy import stats

def audit_report(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: missingness, dtype, skew and outlier count.

    Outliers = values outside Q1 - 1.5*IQR and Q3 + 1.5*IQR.
    Skew and outliers are left empty for columns that are not numbers.
    """
    rows = []
    for col in df.columns:
        missing = df[col].isna().sum()
        dtype = str(df[col].dtype)
        skew = None
        outliers = None
        if dtype in ["int64", "float64"]:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            skew = df[col].skew()
            outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
        rows.append([col, missing, dtype, skew, outliers])
    return pd.DataFrame(rows, columns=["column", "missing", "dtype", "skew", "outliers"]).set_index("column")


def robust_mean(x: pd.Series, method: str = "median") -> float:
    """A robust centre for x. method: "median", "trimmed" or your exclusion rule.

    "exclude" is my B2B rule from Phase 2: drop orders above $500, then take the mean.
    """
    x = pd.Series(x).dropna()
    if method == "median":
        return float(np.median(x))
    elif method == "trimmed":
        return float(stats.trim_mean(x, 0.1))
    elif method == "exclude":
        return float(x[x <= 500].mean())
    else:
        raise ValueError("method should be median, trimmed or exclude")


if __name__ == "__main__":
    # A short demonstration that runs when the file is run as a script
    orders = pd.Series([25, 38, 42, 45, 51, 60, 73, 90, 120, 1800])
    print("plain mean:", orders.mean())
    print("median:", robust_mean(orders, "median"))
    print("trimmed:", robust_mean(orders, "trimmed"))
    print("exclude:", robust_mean(orders, "exclude"))
