import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, mean_squared_error
from app.core.logger import logger


def detect_task_type(df:pd.DataFrame , target_col:str)->str:
    series = df[target_col].dropna()
    unique_count = series.nunique()
    total_count = len(series)

    if series.dtype == "object" or series.dtype.name == "category":
        return "classification" 
    if unique_count/total_count < 0.05 and unique_count<20:
        return "classification"
    return "regression"


def smart_preprocessing(df:pd.DataFrame ,target_col:str)->pd.DataFrame:

    # 1. Feature Selection: Remove IDs or High-Unique Strings
    for col in df.columns:
        if col!=target_col and df[col].dtype == "object" and df[col].nunique() > (len(df)*0.05):
            df.drop(columns=[col],inplace = True)
            logger.info(f"Dropped potential ID column: {col}")
    
    # 2. Adaptive Imputation
        if df[col].isnull().sum() > 0:
            if df[col].dtype in ['int64' , 'float64']:
                fill_val = df[col].median() if abs(df[col].skew()) > 1 else df[col].mean()
                df[col].fillna(fill_val,inplace = True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

    # 3. catgorical encoding
    le_dict = {}
    for col in df.select_dtypes(include = ["object"]).columns:
        if col!=target_col:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype("str"))
            le_dict[col] = le 

    return df,le_dict


def run_ml_pipeline(df: pd.DataFrame) -> dict:
    try:
        target_column = df.columns[-1]
        unique_values = df[target_column].nunique()
        dtype = df[target_column].dtype
    
        task_type = detect_task_type(df,target_column)
        if task_type == "classification" and y.dtype == "object":
            if unique_values > 50:
                return {"error": "Target column has too many unique values — skipping ML"}
        logger.info(f"Detected Task: {task_type}")
        df_clean,encoders = smart_preprocessing(df, target_column)
        X = df_clean.drop(columns = [target_column])
        y = df_clean[target_column]

        if X.empty or len(X) < 10:
            return {"error": "Not enough data to train"}
        X_train,X_test, y_train,y_test = train_test_split(X,y,test_size=0.2 ,random_state=42)
        if task_type == "classification" and y.dtype == "object":
            target_le = LabelEncoder()
            y = target_le.fit_transform(y)

        if task_type == "classification":
            models = {
                "LogisticRegression" : LogisticRegression(max_iter=1000),
                "RandomForestClassifier": RandomForestClassifier(n_estimators=100, random_state=42)
            }       
        else:
            models = {
                "LinearRegression"     : LinearRegression(),
                "RandomForestRegressor": RandomForestRegressor(n_estimators=100, random_state=42)
            }
        results = {}
        for name ,model in models.items():
            model.fit(X_train,y_train)
            preds = model.predict(X_test)
            if task_type == "classification":
                results[name] = {"score" : f1_score(y_test,preds, average= "weighted"), "model" : model}
            else:
                results[name] = {
                                    "score" : np.sqrt(mean_squared_error(y_test,preds)), 
                                    "model": model
                                }
            

        if task_type == "classification":
            best_name = max(results, key = lambda x:results[x]['score'])
        else:
            best_name = min(results, key = lambda x:results[x]['score'])

        best_model = results[best_name]['model']
        best_score = results[best_name]['score']

        #feature importance
        if hasattr(best_model, "feature_importances_"):  
            importance = best_model.feature_importances_
        else:
            importance = abs(best_model.coef_[0]) if hasattr(best_model,"coef_") else np.ones(X.shape[1])

        feature_importance = dict(sorted(zip(X.columns, importance.round(4)), key=lambda x: x[1], reverse=True))
        
        metric_name = "f1_score" if task_type == "classification" else "rmse"

        if task_type == "classification":
            why = (
                f"Target column '{target_column}' has {unique_values} unique values → classification task. "
                f"{best_name} selected with F1 score of {round(best_score, 2)}."
        )
        else:
            why = (
                f"Target column '{target_column}' is continuous → regression task. "
                f"{best_name} selected with RMSE of {round(best_score, 2)}."
        )
        return {
        "task_type"          : task_type,
        "target_column"      : target_column,
        "model_used"         : best_name,
        "why_selected"       : why,
        "metric_name"        : "f1_score" if task_type == "classification" else "rmse",
        "metric_value"       : round(best_score, 4),
        "feature_importance" : feature_importance
        }

    except Exception as e:
        logger.error(f"ML pipeline failed: {str(e)}")
        return {"error": str(e)}





    

    





    
