from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('sLogger')

login_manager = LoginManager()
login_manager.login_view = "login"

bcrypt = Bcrypt()


def create_app(config_filename):
    """
    Create and configure a Flask application.

    This function sets up a Flask application with configurations from a given
    configuration file, initializes extensions (database, login manager, bcrypt),
    registers blueprints, and sets up Flask-Admin with views for models.

    Args:
        config_filename (str): The path to the configuration file.

    Returns:
        Flask: The configured Flask application instance.

    Functionality:
    1. Creates a Flask application instance.
    2. Loads configuration settings from the specified file.
    3. Initializes extensions:
       - SQLAlchemy database instance
       - Login manager
       - Bcrypt for password hashing
    4. Registers the blueprint for the book system project.
    5. Sets up the Flask-Admin interface and adds views for the following models:
       - User
       - Book
       - Rating
       - Author
       - Genre
       - ToRead
       - Review
    """
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    from book_system_project.models import db
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from book_system_project.blueprints import bp
        app.register_blueprint(bp)

        from flask_admin import Admin
        from book_system_project.models import User, Book, Rating, Author, Genre, ToRead, Review
        admin = Admin(app, name='Book System', template_mode='bootstrap3')
        from flask_admin.contrib.sqla import ModelView
        admin.add_view(ModelView(User, db.session))
        admin.add_view(ModelView(Book, db.session))
        admin.add_view(ModelView(Rating, db.session))
        admin.add_view(ModelView(Author, db.session))
        admin.add_view(ModelView(Genre, db.session))
        admin.add_view(ModelView(ToRead, db.session))
        admin.add_view(ModelView(Review, db.session))
    return app
