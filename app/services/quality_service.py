import pandas as pd
import numpy as np
from scipy.stats import skew

def calculate_quality_score(df: pd.DataFrame) -> dict:
    missing_ratio  = df.isnull().sum().sum()/df.size
    missing_score = (1- missing_ratio)*100

    if not df.empty:
        duplicate_ratio = df.duplicated().sum()/len(df)
        duplicate_score = (1-duplicate_ratio)*100
    else:
        duplicate_score = 100

    numeric_df = df.select_dtypes(include="number")
    Q1  = numeric_df.quantile(0.25)
    Q3  = numeric_df.quantile(0.75)
    IQR = Q3 - Q1   
    outliers = (numeric_df < (Q1 -1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR)) 
    outlier_count = outliers.sum().sum()

    total_numeric_cells = numeric_df.size
    if total_numeric_cells > 0:
        outlier_ratio = outlier_count / total_numeric_cells
        outlier_score = (1 - outlier_ratio) * 100
    else:
        outlier_score = 100



    if not numeric_df.empty:
        avg_skew = numeric_df.apply(lambda x:abs(skew(x.dropna()))).mean()
        skewness_score = max(0, 100 - (avg_skew * 20))
    else:
        skewness_score = 100
    

    weights = {
        "missing": 0.35,
        "duplicate": 0.25,
        "outlier": 0.25,
        "skewness": 0.15,
        "total":1
    }

    final_score = (
        (missing_score * weights["missing"]) +
        (duplicate_score * weights["duplicate"]) +
        (outlier_score * weights["outlier"]) +
        (skewness_score * weights["skewness"])
    )

    overall = int(round(final_score))
    if overall >= 80:
        verdict = "Good quality data"
    elif overall >= 60:
        verdict = "Moderate quality — needs attention"
    else:
        verdict = "Poor quality — significant issues found"

    return{
        "overall": overall,
        "breakdown":{
            "missing_score": round(missing_score, 2),
            "duplicate_score": round(duplicate_score, 2),
            "outlier_score": round(outlier_score, 2),
            "skewness_score": round(skewness_score, 2),
        },
        "verdict": verdict
    }
