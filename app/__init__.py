from flask import Flask
import os


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    from app.config.settings import Config
    app.config.from_object(Config)

    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes import ocr_routes, health_routes
    app.register_blueprint(health_routes.bp)
    app.register_blueprint(ocr_routes.bp)

    # Register error handlers
    from app.routes import error_handlers
    error_handlers.register_error_handlers(app)

    return app
