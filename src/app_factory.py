from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from src.config.settings import settings
from src.utils.logger import setup_logging, get_logger

# Extensions
db = SQLAlchemy()
redis_client = None

logger = get_logger(__name__)

def create_app(config_override=None):
    setup_logging()
    
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    if config_override:
        app.config.update(config_override)
        
    # Initialize extensions
    db.init_app(app)
    
    global redis_client
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
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
