from flask_login import UserMixin, current_user
from book_system_project import db, app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


book_genres = db.Table('book_genres',
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                       db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    genres = db.relationship('Genre', secondary=book_genres, back_populates='books', lazy=True)
    rating = db.relationship("Rating", backref="book", lazy=True)
    toreads = db.relationship("ToRead", backref="book", lazy=True)
    reviews = db.relationship("Review", backref="book", lazy=True)

    @property
    def avg_rating(self):
        if not self.rating:
            return None
        total_ratings = sum(rating.rating for rating in self.rating)
        return round(total_ratings / len(self.rating), 2)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(36), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    rating = db.relationship("Rating", backref="user", lazy=True)
    toreads = db.relationship("ToRead", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    books = db.relationship('Book', backref="author", lazy=True)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    books = db.relationship('Book', secondary=book_genres, back_populates='genres', lazy=True)


class ToRead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toread = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.name == "Admin"


admin = Admin(app)

admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Book, db.session))
admin.add_view(AdminModelView(Rating, db.session))
admin.add_view(AdminModelView(Author, db.session))
admin.add_view(AdminModelView(Genre, db.session))
admin.add_view(AdminModelView(ToRead, db.session))
admin.add_view(AdminModelView(Review, db.session))
