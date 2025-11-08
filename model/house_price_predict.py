import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


data = pd.read_csv('data.csv')

SELECTED_FEATURES = [
    'LotArea', 'GrLivArea', 'TotalBsmtSF',
    'YearBuilt', 'YearRemodAdd',
    'FullBath', 'BedroomAbvGr',
    'OverallQual', 'OverallCond',
    'GarageCars'
]

# Check Missing
# print(data[SELECTED_FEATURES].isnull().sum().sum())

target = 'SalePrice'
x = data[SELECTED_FEATURES]
y = np.log1p(data[target])
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

num_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])


pipeline = Pipeline(steps=[
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
    n_iter=50,
    cv=5,
    scoring='r2',
    n_jobs=-1,
    verbose=2,
    random_state=42
)

# Huấn luyện
search.fit(x_train, y_train)

# Kết quả
best_model = search.best_estimator_
print("Best parameters:", search.best_params_)

# Dự đoán và đánh giá
y_pred = best_model.predict(x_test)
y_pred_real = np.expm1(y_pred)
y_test_real = np.expm1(y_test)

print("MAE:", mean_absolute_error(y_test_real, y_pred_real))
print("MSE:", mean_squared_error(y_test_real, y_pred_real))
print("R2:", r2_score(y_test_real, y_pred_real))

# Lưu mô hình
joblib.dump(best_model, "model.pkl")