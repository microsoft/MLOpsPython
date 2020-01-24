import sys
import os
import numpy as np
from azureml.core.run import Run
from unittest.mock import Mock
sys.path.append(os.path.abspath(
        "./diabetes_regression/training"))  # NOQA: E402
from train import train_model


def test_train_model():
    X_train = np.array([1, 2, 3, 4, 5, 6]).reshape(-1,  1)
    y_train = np.array([10, 9, 8, 8, 6, 5])
    X_test = np.array([3, 4]).reshape(-1,  1)
    y_test = np.array([8, 7])
    data = {"train": {"X": X_train, "y": y_train},
            "test": {"X": X_test, "y": y_test}}

    run = Mock(Run)
    reg = train_model(run, data, alpha=1.2)

    run.log.assert_called_with("mse", 0.029843893480256872,
                               description='Mean squared error metric')

    preds = reg.predict([[1], [2]])
    np.testing.assert_equal(preds, [9.93939393939394, 9.03030303030303])
