import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import json

# Supported ML models
MODELS = {
    "random_forest": RandomForestRegressor(),
    "xgboost": XGBRegressor(),
    "logistic_regression": LogisticRegression()
}

def preprocess_data(df, target):
    """Handles missing values, encoding, and feature scaling."""
    y = df[target]
    X = df.drop(columns=[target])

    cat_features = X.select_dtypes(include=["object"]).columns.tolist()
    num_features = X.select_dtypes(exclude=["object"]).columns.tolist()

    transformer = ColumnTransformer([
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
    ])

    return X, y, transformer

def train(data_path: str, target: str, algorithm: str = "random_forest", test_size=0.2):
    """Train an ML model and store performance for dashboard."""
    df = pd.read_csv(data_path)
    X, y, transformer = preprocess_data(df, target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = MODELS.get(algorithm)
    if model is None:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(MODELS.keys())}.")

    pipeline = Pipeline([
        ("transform", transformer),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)
    joblib.dump(pipeline, "model.pkl")

    y_pred = pipeline.predict(X_test)

    if algorithm == "logistic_regression":
        metric = accuracy_score(y_test, y_pred.round())
        metric_name = "Accuracy"
    else:
        metric = mean_squared_error(y_test, y_pred, squared=False)
        metric_name = "RMSE"

    # Store performance in a JSON file for the dashboard
    performance_data = {"Model": algorithm, metric_name: round(metric, 4)}
    with open("model_performance.json", "w") as f:
        json.dump(performance_data, f)

    print(f"Model trained: {algorithm} | {metric_name}: {round(metric, 4)}")
    return pipeline, performance_data
