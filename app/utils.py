import joblib
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app

FEATURE_NAMES = [
    'LotArea', 'GrLivArea', 'TotalBsmtSF',
    'YearBuilt', 'YearRemodAdd',
    'FullBath', 'BedroomAbvGr',
    'OverallQual', 'OverallCond',
    'GarageCars'
]

def load_model():
    try:
        model_path = current_app.config['MODEL_PATH']
        model = joblib.load(model_path)
        return model
    except Exception as e:
        print(f'Model load error: {e}')
        return None

def predict_price(model, features):
    if model is None:
        return 0.0
    try:
        X = pd.DataFrame([features], columns=FEATURE_NAMES)
        prediction = model.predict(X)[0]
        return float(prediction)
    except Exception as e:
        print(f'Prediction error: {e}')
        return 0.0

def allowed_file(filename):
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"uploads/{filename}"
    return None
