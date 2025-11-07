from flask import Flask

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    from .config import Config
    app.config.from_object(Config)
    
    from .models import init_db
    init_db()
    
    from .routes.auth import auth_bp
    from .routes.buyer import buyer_bp, house_bp
    from .routes.seller import seller_bp
    from .routes.payment import payment_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(house_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(payment_bp)
    
    return app
