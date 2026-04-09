import numpy as np
import pandas as pd 
from app.core.logger import logger

from sklearn.ensemble import IsolationForest


def detect_anomalies(df:pd.DataFrame)->dict:
    try:
        numeric_df = df.select_dtypes(include="number")
        numeric_df = numeric_df.dropna(how = 'all')
        if numeric_df.empty:
            return {
                "method": "IsolationForest",
                "error": "No numeric data available after cleaning"
            }
        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        numeric_df = numeric_df.fillna(numeric_df.median())
        predictions = model.fit_predict(numeric_df)
        anomaly_scores = model.decision_function(numeric_df)

        anomalous_rows_count = int((predictions == -1).sum())
        total_rows = len(numeric_df)

        top_5_pos = np.argsort(anomaly_scores)[:5].tolist()
        top_5_indices = numeric_df.index[top_5_pos].tolist()



        return {
            "method"                : "IsolationForest",
            "total_rows"            : total_rows,
            "anomalous_rows_count"  : anomalous_rows_count,
            "anomaly_percentage"    : round((anomalous_rows_count/total_rows)*100,2),
            "top_anomalous_indices" : top_5_indices     # top 5 row indices,
        }

    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")
        return {
            "error": str(e)
        }


