from hiclass._calibration.BinaryCalibrator import _BinaryCalibrator
from sklearn.isotonic import IsotonicRegression as SkLearnIR
from sklearn.utils.validation import check_is_fitted
import numpy as np


class _IsotonicRegression(_BinaryCalibrator):
    name = "IsotonicRegression"

    def __init__(self, params={}) -> None:
        self._is_fitted = False
        if "out_of_bounds" not in params:
            params["out_of_bounds"] = "clip"
        self.isotonic_regression = SkLearnIR(**params)

    def fit(self, y: np.ndarray, scores: np.ndarray, X: np.ndarray = None):
        self.isotonic_regression.fit(scores, y)
        self._is_fitted = True
        return self

    def predict_proba(self, scores: np.ndarray, X: np.ndarray = None):
        check_is_fitted(self)
        return self.isotonic_regression.predict(scores)
