"""Initialize Flask application and extensions."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register custom template filters
    from .utils import hex_to_rgb, month_name
    app.jinja_env.filters['hex_to_rgb'] = hex_to_rgb
    app.jinja_env.filters['month_name'] = month_name

    with app.app_context():
        # Import models and routes
        from . import models  # noqa
        from .routes import auth, main, expenses, budgets, reports
        
        # Register blueprints
        app.register_blueprint(auth.bp, url_prefix='/auth')
        app.register_blueprint(main.bp, url_prefix='/')
        app.register_blueprint(expenses.bp, url_prefix='/expenses')
        app.register_blueprint(budgets.bp, url_prefix='/budgets')
        app.register_blueprint(reports.bp, url_prefix='/reports')
        
        return app