import numpy as np
from diabetes_regression.training.train import train_model, get_model_metrics


def get_test_data():
    X_train = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    y_train = np.array([10, 9, 8, 8, 6, 5])
    X_test = np.array([3, 4]).reshape(-1, 1)
    y_test = np.array([8, 7])
    data = {"train": {"X": X_train, "y": y_train},
            "test": {"X": X_test, "y": y_test}}
    return data


class MockModel:

    @staticmethod
    def predict(data):
        return ([8.12121212, 7.21212121])


def test_train_model():
    reg_model = train_model(get_test_data(), {"alpha": 1.2})

    preds = reg_model.predict([[1], [2]])
    np.testing.assert_equal(preds, [9.93939393939394, 9.03030303030303])


def test_get_model_metrics():
    metrics = get_model_metrics(MockModel(), get_test_data())

    assert 'mse' in metrics
    mse = metrics['mse']
    np.testing.assert_almost_equal(mse, 0.029843893480257067)
