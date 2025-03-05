import joblib
import xgboost as xgb
import numpy as np
import pandas as pd
import pkg_resources


def predict_iimi(newdata: pd.DataFrame, method: str = "xgb",
                 trained_model=None, report_virus_level: bool = True):
    """
    predict_iimi(newdata: pd.DataFrame, method: str = "xgb",
                 trained_model=None, report_virus_level: bool = True)

    Uses a machine learning model to predict the infection status for the plant sample(s).
    Can use custom model or default models for rf, xgb, or en.

    Parameters:
        newdata (pd.DataFrame): Input data containing features and metadata.
        method (str): The machine learning method, either 'rf', 'xgb', or 'en'.
        trained_model: The pre-trained model to use. If None, default models are used.
        report_virus_level (bool): If True, return aggregated results by virus.

    Returns:
        pd.DataFrame: The predictions for each sample at the segment or virus level.
    """
    required_columns = ['sample_id', 'virus_name', 'iso_id', 'seg_id']
    if not all(col in newdata.columns for col in required_columns):
        raise ValueError("Missing required columns:",
                         "".join(required_columns))

    # prep the feature matrix by removing the first 4 columns, make sure feature names match, and only this feature is used
    X = newdata.drop(columns=required_columns)
    if "mapped_read_proportion" not in X.columns:
        raise ValueError(
            "The required feature 'mapped_read_proportion' is missing from the prediction data.")
    X = X[["mapped_read_proportion"]]

    result_df = pd.DataFrame({
        'Sample_ID': newdata['sample_id'],
        'Virus_name': newdata['virus_name'],
        'Isolate_ID': newdata['iso_id'],
        'Segment_ID': newdata['seg_id']
    })

    if method == "rf":
        if trained_model is None:
            model = joblib.load(pkg_resources.resource_filename(
                'iimi.data', 'trained_rf.pkl'))

        else:
            model = trained_model

        prediction = model.predict_proba(X)
        if prediction.shape[1] == 1:
            result_df['Probability'] = 1 - prediction[:, 0]
        else:
            result_df['Probability'] = prediction[:, 1]  # class 1 probability

        # convert probability to binary prediction
        result_df['Prediction'] = result_df['Probability'] > 0.5

    elif method == "xgb":
        if trained_model is None:
            model = xgb.Booster()
            model = joblib.load(pkg_resources.resource_filename(
                'iimi.data', 'trained_xgb.model'))
        else:
            model = trained_model

        dmatrix = xgb.DMatrix(X)
        prediction = model.predict(dmatrix)
        result_df['Probability'] = prediction
        result_df['Prediction'] = prediction > 0.5

    elif method == "en":
        if trained_model is None:
            model = joblib.load(pkg_resources.resource_filename(
                'iimi.data', 'trained_en.pkl'))
        else:
            model = trained_model

        # check if intercept in traning, then add same to prediction
        X_with_intercept = np.c_[np.ones(X.shape[0])]
        prediction = model.predict(X_with_intercept)
        result_df['Probability'] = prediction
        result_df['Prediction'] = prediction > 0.5

    else:
        raise ValueError("`method` must be 'rf', 'xgb', or 'en'.")

    # if report_virus_level is True, aggregate results by virus
    if report_virus_level:
        result_df = result_df.groupby(['Sample_ID', 'Virus_name'], as_index=False).agg(
            Virus_name=('Virus_name', 'first'),
            Segment_ID=('Segment_ID', 'first'),
            Isolate_ID=('Isolate_ID', 'first'),
            # 'any' gives aggregated True if any True prediction
            Prediction=('Prediction', 'any')
        )

    return result_df


if __name__ == "__main__":

    # example usage
    # 1: using random forest model
    print("\n1: random forest model")
    newdata_rf = pd.DataFrame({
        'sample_id': ['S1', 'S2'],
        'virus_name': ['VirusA', 'VirusB'],
        'iso_id': ['iso1', 'iso2'],
        'seg_id': ['seg1', 'seg2'],
        'mapped_read_proportion': [0.8, 0.9]
    })
    result_rf = predict_iimi(newdata_rf, method='rf',
                             trained_model=None, report_virus_level=True)
    print(result_rf)

    # 2: using XGBoost model
    print("\n2: XGBoost model")
    newdata_xgb = pd.DataFrame({
        'sample_id': ['S3', 'S4'],
        'virus_name': ['VirusC', 'VirusD'],
        'iso_id': ['iso3', 'iso4'],
        'seg_id': ['seg3', 'seg4'],
        'mapped_read_proportion': [0.75, 0.85]
    })
    result_xgb = predict_iimi(
        newdata_xgb, method='xgb', trained_model=None, report_virus_level=True)
    print(result_xgb)

    # 3: using elastic net model
    print("\n3: elastic net model")
    newdata_en = pd.DataFrame({
        'sample_id': ['S5', 'S6'],
        'virus_name': ['VirusE', 'VirusF'],
        'iso_id': ['iso5', 'iso6'],
        'seg_id': ['seg5', 'seg6'],
        'mapped_read_proportion': [0.65, 0.55]
    })
    result_en = predict_iimi(newdata_en, method='en',
                             trained_model=None, report_virus_level=True)
    print(result_en)
