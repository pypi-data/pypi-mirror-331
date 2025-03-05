import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, log_loss, mean_absolute_error, 
    mean_squared_error, r2_score
)

def evaluate_model(eval_type, actual_val, predicted_val, predicted_prob=None):
    """
    Evaluates model performance based on the type (classification/regression).
    
    Args:
        eval_type (str): "classification" or "regression"
        actual_val (list or np.array): Actual values.
        predicted_val (list or np.array): Predicted values.
        predicted_prob (list or np.array, optional): Probability scores for classification (for AUC, Log Loss).
    
    Returns:
        dict: A dictionary containing relevant evaluation metrics.
    """
    if eval_type not in ["classification", "regression"]:
        raise ValueError("Invalid type. Use 'classification' or 'regression'.")

    metrics = {}

    if eval_type == "classification":
        try:
            metrics["accuracy"] = accuracy_score(actual_val, predicted_val)
        except Exception as e:
            metrics["accuracy"] = f"Error: {e}"

        try:
            metrics["precision"] = precision_score(actual_val, predicted_val, average="weighted", zero_division=0)
        except Exception as e:
            metrics["precision"] = f"Error: {e}"

        try:
            metrics["recall"] = recall_score(actual_val, predicted_val, average="weighted", zero_division=0)
        except Exception as e:
            metrics["recall"] = f"Error: {e}"

        try:
            metrics["f1_score"] = f1_score(actual_val, predicted_val, average="weighted", zero_division=0)
        except Exception as e:
            metrics["f1_score"] = f"Error: {e}"

        if predicted_prob is not None:
            try:
                metrics["roc_auc"] = roc_auc_score(actual_val, predicted_prob, multi_class="ovr")
            except Exception as e:
                metrics["roc_auc"] = f"Error: {e}"

            try:
                metrics["log_loss"] = log_loss(actual_val, predicted_prob)
            except Exception as e:
                metrics["log_loss"] = f"Error: {e}"

    elif eval_type == "regression":
        try:
            metrics["mae"] = mean_absolute_error(actual_val, predicted_val)
        except Exception as e:
            metrics["mae"] = f"Error: {e}"

        try:
            metrics["mse"] = mean_squared_error(actual_val, predicted_val)
        except Exception as e:
            metrics["mse"] = f"Error: {e}"

        try:
            metrics["rmse"] = np.sqrt(mean_squared_error(actual_val, predicted_val))
        except Exception as e:
            metrics["rmse"] = f"Error: {e}"

        try:
            metrics["r2_score"] = r2_score(actual_val, predicted_val)
        except Exception as e:
            metrics["r2_score"] = f"Error: {e}"

        try:
            n = len(actual_val)
            p = 1  # Assuming single predictor
            r2 = r2_score(actual_val, predicted_val)
            metrics["adjusted_r2"] = 1 - ((1 - r2) * (n - 1) / (n - p - 1))
        except Exception as e:
            metrics["adjusted_r2"] = f"Error: {e}"

        try:
            metrics["mape"] = np.mean(np.abs((actual_val - predicted_val) / actual_val)) * 100
        except Exception as e:
            metrics["mape"] = f"Error: {e}"

    return metrics
