import os

BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = 'test'
    
    BASE_DIR = BASE
    MODEL_PATH = os.path.join(BASE, 'model', 'model.pkl')
    DB_PATH = os.path.join(BASE, 'predictions.db')
    UPLOAD_FOLDER = os.path.join(BASE, 'static', 'uploads')
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
