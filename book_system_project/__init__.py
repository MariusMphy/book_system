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
