import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder

# from ydata_profiling import ProfileReport

data = pd.read_csv('data.csv')
# profile = ProfileReport(data, title='House Price Report', explorative=True)
# profile.to_file('house_price_report.html')

target = 'SalePrice'
x = data.drop(target, axis=1)
y = np.log1p(data[target])
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


numerical_features = [
    'LotFrontage', 'LotArea', 'MasVnrArea',
    'BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF',
    '1stFlrSF', '2ndFlrSF', 'LowQualFinSF', 'GrLivArea',
    'GarageArea', 'WoodDeckSF', 'OpenPorchSF',
    'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea',
    'YearBuilt', 'YearRemodAdd', 'GarageYrBlt',
    'BsmtFullBath', 'BsmtHalfBath', 'FullBath', 'HalfBath',
    'BedroomAbvGr', 'KitchenAbvGr', 'TotRmsAbvGrd',
    'Fireplaces', 'GarageCars',
    'MiscVal', 'MoSold', 'YrSold'
]
ordinal_features_dict = {
    'ExterQual': ['Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'ExterCond': ['Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'BsmtQual': ['NA', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'BsmtCond': ['NA', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'HeatingQC': ['Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'KitchenQual': ['Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'FireplaceQu': ['NA', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'GarageQual': ['NA', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'GarageCond': ['NA', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
    'PoolQC': ['NA', 'Fa', 'TA', 'Gd', 'Ex'],
    'BsmtExposure': ['NA', 'No', 'Mn', 'Av', 'Gd'],
    'BsmtFinType1': ['NA', 'Unf', 'LwQ', 'Rec', 'BLQ', 'ALQ', 'GLQ'],
    'BsmtFinType2': ['NA', 'Unf', 'LwQ', 'Rec', 'BLQ', 'ALQ', 'GLQ'],
    'GarageFinish': ['NA', 'Unf', 'RFn', 'Fin'],
    'Functional': ['Sal', 'Sev', 'Maj2', 'Maj1', 'Mod', 'Min2', 'Min1', 'Typ'],
    'Fence': ['NA', 'MnWw', 'GdWo', 'MnPrv', 'GdPrv'],
    'LotShape': ['IR3', 'IR2', 'IR1', 'Reg'],
    'LandSlope': ['Gtl', 'Mod', 'Sev'],
    'PavedDrive': ['N', 'P', 'Y'],
    'CentralAir': ['N', 'Y']
}
ordinal_features = list(ordinal_features_dict.keys())
nominal_features = [
    'MSSubClass', 'MSZoning', 'Street', 'Alley', 'LandContour',
    'LotConfig', 'Neighborhood', 'Condition1', 'Condition2',
    'BldgType', 'HouseStyle', 'RoofStyle', 'RoofMatl',
    'Exterior1st', 'Exterior2nd', 'MasVnrType', 'Foundation',
    'Heating', 'Electrical', 'GarageType', 'SaleType',
    'SaleCondition', 'MiscFeature'
]
# Thêm OverallQual và OverallCond vào ordinal
ordinal_features_dict['OverallQual'] = list(range(1, 11))
ordinal_features_dict['OverallCond'] = list(range(1, 11))
ordinal_features.extend(['OverallQual', 'OverallCond'])

# Xử lí numerical
num_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

ordinal_categories = [ordinal_features_dict[f] for f in ordinal_features if f in x.columns]
ord_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
    ('encoder', OrdinalEncoder(
        categories=ordinal_categories,
        handle_unknown='use_encoded_value',
        unknown_value=-1
    ))
])

nom_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

#Column transformer
preprocessor = ColumnTransformer(transformers=[
    ('num_feature', num_transformer, numerical_features),
    ('ord_feature', ord_transformer, ordinal_features),
    ('nom_feature', nom_transformer, nominal_features),
])


reg = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor())
])

# reg.fit(x_train, y_train)
#
# y_predict = reg.predict(x_test)
#
# y_test_real = np.expm1(y_test)
# y_predict_real = np.expm1(y_predict)
# for i, j in zip(y_predict_real, y_test_real):
#     print('Predicted value: {}. Actual Value: {}'.format( i, j))
#
# print('MAE: ', mean_absolute_error(y_test_real, y_predict_real))
# print('MSE: ', mean_squared_error(y_test_real, y_predict_real))
# print('R2: ', r2_score(y_test_real, y_predict_real))

params = {
    'model__n_estimators': [100, 200],
    'model__criterion': ['squared_error', 'absolute_error'],
    'model__max_depth': [None, 2, 5]
}
grid_search = RandomizedSearchCV(
    estimator=reg, param_distributions=params, cv=5, n_iter=20, scoring='r2', verbose=2, n_jobs=-1
)

grid_search.fit(x_train, y_train)
print(grid_search.best_params_)
print(grid_search.best_score_)

# Lưu mô hình tốt nhất ra file .pkl
import joblib, os
os.makedirs("model", exist_ok=True)
joblib.dump(grid_search.best_estimator_, "model.pkl")
print("Mô hình đã được lưu vào: model/model.pkl")

# Đánh giá
y_predict = grid_search.predict(x_test)
y_predict_real = np.expm1(y_predict)
y_test_real = np.expm1(y_test)
print('MAE: {}'.format(mean_absolute_error(y_test_real, y_predict_real)))
print('MSE: {}'.format(mean_squared_error(y_test_real, y_predict_real)))
print('R2: {}'.format(r2_score(y_test_real, y_predict_real)))