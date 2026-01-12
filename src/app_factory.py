from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from src.config.settings import settings
from src.utils.logger import setup_logging, get_logger

# Extensions
db = SQLAlchemy()

logger = get_logger(__name__)

def create_app(config_override=None):
    setup_logging()
    
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REDIS_URL"] = settings.REDIS_URL
    
    if config_override:
        app.config.update(config_override)
        
    # Initialize extensions
    db.init_app(app)
    
    from src.extensions.redis_ext import redis_manager
    redis_manager.init_app(app)
    
    # Register Blueprints
    from src.controllers.wechat_ctrl import wechat_bp
    from src.controllers.api_ctrl import api_bp
    
    app.register_blueprint(wechat_bp)
    app.register_blueprint(api_bp)
    
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"})

    logger.info("Application factory created the app instance.")
    return app
