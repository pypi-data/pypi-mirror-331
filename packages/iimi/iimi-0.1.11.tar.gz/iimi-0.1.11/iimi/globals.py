import joblib
import xgboost as xgb
import importlib.resources


def load_data(filename):
    with importlib.resources.path('iimi.data', filename) as path:
        return joblib.load(path)


nucleotide_info = load_data('nucleotide_info.pkl')

unreliable_regions = load_data('unreliable_regions.pkl')

trained_rf = load_data('trained_rf.pkl')

trained_xgb = xgb.Booster()
with importlib.resources.path('iimi.data', 'trained_xgb.model') as path:
    trained_xgb.load_model(path)

trained_en = load_data('trained_en.pkl')

example_diag = load_data('example_diag.pkl')

example_cov = load_data('example_cov.pkl')
