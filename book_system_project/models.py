from flask_login import UserMixin
from book_system_project import db
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, EmailField, PasswordField, SelectField, FloatField, TextAreaField


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)

    author_id = db.Column(db.Integer, db.ForeighKey("author.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)

    rating = db.relationship("Rating", backref="book", lazy=True)


    # user_favorites = ()
    # user_read_list = ()
    # user_review = ()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    # more user info add later, now make relations

    rating = db.relationship("Rating", backref="user", lazy=True)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer(5))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nuullable=False)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    books = db.relationship('Book', backref="author", lazy=True)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    books = db.relationship("Book", backref="genre", lazy=True)
