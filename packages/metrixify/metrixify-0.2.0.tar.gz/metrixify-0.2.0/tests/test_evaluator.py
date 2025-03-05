import pytest
import numpy as np
from evalify import evaluate_model

def test_classification_metrics():
    actual = [0, 1, 1, 0, 1]
    predicted = [0, 1, 0, 0, 1]
    
    metrics = evaluate_model("classification", actual, predicted)

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert isinstance(metrics["accuracy"], float)

def test_regression_metrics():
    actual = np.array([3.2, 4.5, 6.1, 7.8, 9.0])
    predicted = np.array([3.0, 4.8, 5.9, 7.5, 9.2])
    
    metrics = evaluate_model("regression", actual, predicted)

    assert "mae" in metrics
    assert "mse" in metrics
    assert "rmse" in metrics
    assert "r2_score" in metrics
    assert isinstance(metrics["mae"], float)

def test_invalid_type():
    actual = [0, 1, 1, 0, 1]
    predicted = [0, 1, 0, 0, 1]

    with pytest.raises(ValueError, match="Invalid type"):
        evaluate_model("invalid_type", actual, predicted)



actual_vals = [0, 1, 1, 0, 1]
predicted_vals = [0, 1, 0, 0, 1]

metrics = evaluate_model("classification", actual_vals, predicted_vals)
print(metrics)

