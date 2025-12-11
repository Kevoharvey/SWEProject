# Machine Learning Code Explanations

## 1. Import Libraries
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')
```
- **pandas**: Used for data manipulation and analysis (DataFrames).
- **numpy**: Fundamental package for scientific computing (arrays, math).
- **matplotlib & seaborn**: Libraries for data visualization.
- **sklearn (Scikit-Learn)**: Provides tools for data analysis and ML models (LinearRegression, RandomForest, metrics, preprocessing).
- **xgboost, lightgbm, catboost**: Gradient boosting frameworks for optimized decision tree algorithms.
- **tensorflow/keras**: Used for building deep learning models (Neural Networks).
- **warnings**: Used to suppress warning messages for a cleaner output.

## 2. Data Preparation
```python
# Handle missing values
for col in X.columns:
    if X[col].isnull().sum() > 0:
        mean_val = X[col].mean()
        X[col] = X[col].fillna(mean_val)
```
- Iterates through each column in the features DataFrame `X`.
- Checks if there are any missing values (`isnull`).
- Calculates the mean (average) of the column.
- Fills missing values with that mean (`fillna`). This is a simple imputation strategy.

## 3. Data Splitting and Scaling
```python
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
```
- Splits the dataset into training (80%) and validation (20%) sets.
- `random_state=42` ensures reproducibility (same split every time).

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
```
- **StandardScaler**: Standardizes features by removing the mean and scaling to unit variance. This is crucial for Neural Networks and distance-based algorithms, though less critical for tree-based models (RF, XGBoost).
- `fit_transform` calculates parameters from training data and scales it.
- `transform` uses those same parameters to scale validation data.

## 4. Model Training

### Random Forest
```python
rf_model = RandomForestRegressor(n_estimators=200, max_depth=15, ...)
rf_model.fit(X_train, y_train)
```
- **RandomForestRegressor**: An ensemble method using multiple decision trees.
- `n_estimators=200`: Creates 200 trees.
- `max_depth=15`: Limits tree depth to prevent overfitting.
- `.fit()`: Trains the model on the training data.

### XGBoost (Extreme Gradient Boosting)
```python
xgb_model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.1, ...)
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=True)
```
- **XGBRegressor**: A highly efficient gradient boosting implementation.
- `learning_rate=0.1`: Step size shrinkage used to prevent overfitting.
- `eval_set`: Allows monitoring performance on validation data during training.

### CatBoost (Categorical Boosting) - NEW
```python
cb_model = CatBoostRegressor(iterations=500, learning_rate=0.05, depth=6, ...)
cb_model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
```
- **CatBoostRegressor**: Gradient boosting optimized for categorical features (though we are using numerical here).
- `iterations=500`: Number of trees to build.
- `depth=6`: Depth of the trees.
- excels at handling categorical data automatically (if configured) and often requires less parameter tuning.

### Neural Network (Keras) - NEW
```python
ann_model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(1)
])
```
- **Sequential**: A linear stack of layers.
- **Dense(128)**: A fully connected layer with 128 neurons.
- **activation='relu'**: Rectified Linear Unit activation function (introduces non-linearity).
- **Dropout(0.2)**: Randomly sets 20% of inputs to 0 during training to prevent overfitting.
- **Dense(1)**: Output layer with 1 neuron (predicting a single continuous value: Price).

```python
ann_model.compile(optimizer=Adam(learning_rate=0.01), loss='mean_squared_error')
ann_model.fit(X_train_scaled, y_train, ...)
```
- **compile**: Configures the model for training.
- **Adam**: A popular optimization algorithm.
- **loss='mean_squared_error'**: The objective function the model tries to minimize.

## 5. Model Comparison
```python
df_comparison = pd.DataFrame(comparison_data)
df_comparison = df_comparison.sort_values('Val RMSE')
```
- Collects metrics (RMSE, MAE, R2) from all models into a dictionary.
- Creates a DataFrame for easy viewing.
- Sorts by **Validation RMSE** (Root Mean Squared Error) to show the best performing model at the top (lowest error).

## 6. Feature Importance
```python
importance = model.feature_importances_
```
- Extracts which features contributed most to the model's predictions.
- **Note**: This works for Tree-based models (RF, XGBoost, CatBoost) but not directly for standard Keras Neural Networks without additional interpretation tools (like SHAP or permutation importance).
