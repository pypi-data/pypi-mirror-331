from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import ElasticNetCV
import xgboost as xgb
from sklearn.preprocessing import StandardScaler


def train_iimi(train_x: pd.DataFrame, train_y: pd.Series, method: str = "xgb",
               nrounds: int = 100, min_child_weight: int = 10, gamma: int = 20,
               ntree: int = 200, mtry: int = 10, k: int = 5, **kwargs):
    """
    train_iimi(train_x: pd.DataFrame, train_y: pd.Series, method: str = "xgb",
               nrounds: int = 100, min_child_weight: int = 10, gamma: int = 20,
               ntree: int = 200, mtry: int = 10, k: int = 5, **kwargs)

    Trains a `XGBoost` (default), `Random Forest`, or `Elastic Net` model using user-provided data.

    Parameters:
        train_x: pd.DataFrame, features for training.
        train_y: pd.Series, labels for training.
        method: str, choice of model: 'rf' (Random Forest), 'xgb' (XGBoost), 'en' (Elastic Net).
        nrounds: int, number of boosting rounds for 'xgb'.
        min_child_weight: int, min child weight for 'xgb'.
        gamma: int, gamma for 'xgb'.
        ntree: int, number of trees for 'rf'.
        mtry: int, number of features for Random Forest.
        k: int, number of folds for cross-validation in 'en'.
        **kwargs: Additional arguments for the models.

    Returns:
        Trained model (Random Forest, XGBoost, or Elastic Net).
    """

    if method == "rf":
        model = RandomForestClassifier(
            n_estimators=ntree, max_features=mtry, **kwargs)
        model.fit(train_x, train_y)

    elif method == "xgb":
        xgbtrain = StandardScaler().fit_transform(train_x)
        xgblabel = train_y.astype(int)
        model = xgb.XGBClassifier(
            objective="binary:logistic",
            n_estimators=nrounds,
            min_child_weight=min_child_weight,
            gamma=gamma,
            **kwargs
        )
        model.fit(xgbtrain, xgblabel)

    elif method == "en":
        model = ElasticNetCV(cv=StratifiedKFold(
            n_splits=k), max_iter=10000, **kwargs)
        model.fit(train_x, train_y)

    else:
        raise ValueError("`method` must be 'rf', 'xgb', or 'en'.")

    return model


if __name__ == "__main__":

    # example usage
    train_x = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'feature3': np.random.rand(100),
        'feature4': np.random.rand(100)
    })
    train_y = pd.Series(np.random.choice([0, 1], size=100))

    # 1: using random forest model
    print("\n1. random forest Model:")
    rf_model = train_iimi(train_x, train_y, method="rf", ntree=100, mtry=2)
    rf_predictions = rf_model.predict(train_x)
    print(f"predictions on training data: {rf_predictions[:10]}")
    rf_accuracy = accuracy_score(train_y, rf_predictions)
    print(f"model accuracy: {rf_accuracy:.4f}")

    # 2: using XGBoost model
    print("\n2. XGBoost model:")
    xgb_model = train_iimi(train_x, train_y, method="xgb", nrounds=100)
    xgb_predictions = xgb_model.predict(train_x)
    print(f"predictions on training data: {xgb_predictions[:10]}")
    xgb_accuracy = accuracy_score(train_y, xgb_predictions)
    print(f"model accuracy: {xgb_accuracy:.4f}")

    # 3: using elastic net model
    print("\n3. elastic net model:")
    en_model = train_iimi(train_x, train_y, method="en", k=5)
    en_predictions = en_model.predict(train_x)
    print(f"predictions on training data: {en_predictions[:10]}")
    # to use classification accuracy, convert continuous predictions to binary
    binary_en_predictions = (en_predictions >= 0.5).astype(int)
    en_accuracy = accuracy_score(train_y, binary_en_predictions)
    print("emodel accuracy (binary classification): {:.4f}".format(
        en_accuracy))
    # or use regression metrics
    mse = mean_squared_error(train_y, en_predictions)
    print("model accuracy (regression metric): {:.4f}".format(mse))
