import os

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder


data = pd.read_csv('data.csv')

SELECTED_FEATURES = [
    'LotArea', 'GrLivArea', 'TotalBsmtSF',
    'YearBuilt', 'YearRemodAdd',
    'FullBath', 'BedroomAbvGr',
    'OverallQual', 'OverallCond',
    'GarageCars'
]

target = 'SalePrice'
x = data[SELECTED_FEATURES]
y = np.log1p(data[target])
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('model', RandomForestRegressor(random_state=42, n_jobs=-1))
])


param_distributions = {
    'model__n_estimators': [100, 200, 300],
    'model__max_depth': [None, 5, 10, 20],
    'model__min_samples_split': [2, 5, 10],
    'model__min_samples_leaf': [1, 2, 4],
    'model__criterion': ['squared_error', 'absolute_error']
}

search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    cv=5, n_iter=20, scoring='r2', verbose=2, n_jobs=-1
)

search.fit(x_train, y_train)

print("Best params:", search.best_params_)
print("Best CV R2:", search.best_score_)

y_pred = search.predict(x_test)
y_pred_real = np.expm1(y_pred)
y_test_real = np.expm1(y_test)

print("MAE:", mean_absolute_error(y_test_real, y_pred_real))
print("MSE:", mean_squared_error(y_test_real, y_pred_real))
print("R2:", r2_score(y_test_real, y_pred_real))

os.makedirs("model", exist_ok=True)
joblib.dump(search.best_estimator_, "model.pkl")
print("Mô hình đã được lưu vào: model/model.pkl")