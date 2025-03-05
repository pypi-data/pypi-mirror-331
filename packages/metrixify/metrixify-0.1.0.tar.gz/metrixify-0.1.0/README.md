metrixify 🚀
A lightweight library for automatic model evaluation

📌 Overview
metrixify is an easy-to-use Python library that automatically evaluates machine learning models. It supports both classification and regression models and returns evaluation metrics in a dictionary format.

📥 Installation
You can install metrixify directly from PyPI:

pip install metrixify

🛠 Usage
1️⃣ Import the Library

from metrixify import evaluate_model


2️⃣ Classification Model Evaluation

from metrixify import evaluate_model

actual_vals = [0, 1, 1, 0, 1]
predicted_vals = [0, 1, 0, 0, 1]

metrics = evaluate_model("classification", actual_vals, predicted_vals)
print(metrics)


✅ Output:

{
    'accuracy': 0.8,
    'precision': 0.75,
    'recall': 0.8,
    'f1_score': 0.76,
    'roc_auc': 'Error: Need probability estimates',
    'log_loss': 'Error: Need probability estimates'
}

3️⃣ Regression Model Evaluation

actual_vals = [3.2, 4.5, 6.1, 7.8, 9.0]
predicted_vals = [3.0, 4.8, 5.9, 7.5, 9.2]

metrics = evaluate_model("regression", actual_vals, predicted_vals)
print(metrics)

✅ Output:

{
    'mae': 0.18,
    'mse': 0.036,
    'rmse': 0.19,
    'r2_score': 0.97,
    'adjusted_r2': 0.95,
    'mape': 2.5
}


📊 Supported Metrics
Classification Metrics
✅ Accuracy
✅ Precision (Weighted)
✅ Recall (Weighted)
✅ F1-Score (Weighted)
✅ ROC-AUC (if probability estimates are provided)
✅ Log Loss (if probability estimates are provided)
Regression Metrics
✅ Mean Absolute Error (MAE)
✅ Mean Squared Error (MSE)
✅ Root Mean Squared Error (RMSE)
✅ R² Score
✅ Adjusted R² Score
✅ Mean Absolute Percentage Error (MAPE)
⚡ Features
✅ Automatic Model Evaluation – No need to manually calculate metrics
✅ Error Handling – Any metric failure returns an error message instead of stopping execution
✅ Lightweight & Fast – Simple to install and use

🛠 Contributing
Contributions are welcome! If you find bugs or want to improve metrixify, feel free to fork the repository and submit a pull request.

📜 License
This project is licensed under the MIT License.

🌟 Support
If you like this project, please give it a ⭐ on GitHub!

