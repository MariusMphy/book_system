from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask import flash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


book_genres = db.Table('book_genres',
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                       db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))
"""
Association table for the many-to-many relationship between books and genres.

This table establishes a many-to-many relationship between the `Book` and `Genre` models, 
allowing a book to belong to multiple genres and a genre to include multiple books.

Fields:
    book_id (int): Foreign key referencing the `id` field in the `Book` model. 
                   Primary key to ensure uniqueness in the relationship.
    genre_id (int): Foreign key referencing the `id` field in the `Genre` model. 
                    Primary key to ensure uniqueness in the relationship.
"""


class Book(db.Model):
    """
    Model representing a book in the application.

    Fields:
        id (int): Primary key, unique identifier for each book.
        title (str): The title of the book, maximum length of 256 characters.
        author_id (int): Foreign key referencing the author of the book.

    Relationships:
        genres (list of Genre): Many-to-many relationship with the Genre model.
        rating (list of Rating): One-to-many relationship with the Rating model.
        toreads (list of ToRead): One-to-many relationship with the ToRead model.
        reviews (list of Review): One-to-many relationship with the Review model.

    Methods:
        to_dict(): Returns a dictionary representation of the book instance.

    Properties:
        avg_rating (float): Calculates and returns the average rating of the book, rounded to 2 decimal places.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    genres = db.relationship('Genre', secondary=book_genres, back_populates='books', lazy=True)
    rating = db.relationship("Rating", backref="book", lazy=True)
    toreads = db.relationship("ToRead", backref="book", lazy=True)
    reviews = db.relationship("Review", backref="book", lazy=True)

    def to_dict(self):
        """
        Returns a dictionary representation of the book instance.

        Returns:
            dict: A dictionary containing the book's id, title, and author_id.
        """
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
        }

    @property
    def avg_rating(self):
        """
        Calculates and returns the average rating of the book.

        If the book has no ratings, returns None. Otherwise, computes the average rating
        by summing all rating values and dividing by the number of ratings, rounded to
        2 decimal places.

        Returns:
            float or None: The average rating of the book, or None if there are no ratings.
        """
        if not self.rating:
            return None
        total_ratings = sum(rating.rating for rating in self.rating)
        return round(total_ratings / len(self.rating), 2)


class User(UserMixin, db.Model):
    """
    User model representing a user in the application.

    This model stores user details including email, password, name, phone number, date of birth, and gender.
    It also defines relationships to other models such as Rating, ToRead, and Review.

    Relationships:
    rating (list of Rating): One-to-many relationship with the Rating model, representing ratings given by the user.
    toreads (list of ToRead): One-to-many relationship with the ToRead model, representing books the user wants to read.
    reviews (list of Review): One-to-many relationship with the Review model, representing reviews written by the user.
    """
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
    """
    Rating model representing a user's rating of a book.

    This model stores the rating value given by a user for a specific book and links to the User and Book models.

    Relationships:
        user (User):
            Many-to-one relationship with the `User` model, indicating the user who provided the rating.

        book (Book):
            Many-to-one relationship with the `Book` model, indicating the book that was rated.
    """
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class Author(db.Model):
    """
    Author model representing an author in the application.

    This model stores the author's name and links to the books written by the author.

    Relationships:
        books (list of Book):
            One-to-many relationship with the `Book` model, indicating the books authored by this author.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    books = db.relationship('Book', backref="author", lazy=True)


class Genre(db.Model):
    """
    Genre model representing a genre in the application.

    This model stores the genre's name and links to the books associated with this genre.

    Relationships:
        books (list of Book):
            Many-to-many relationship with the `Book` model through the `book_genres` association table,
            indicating the books that belong to this genre.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    books = db.relationship('Book', secondary=book_genres, back_populates='genres', lazy=True)


class ToRead(db.Model):
    """
    ToRead model representing a book that a user wants to read.

    This model stores the status of whether the book is marked as "to-read" by the user and links to both the user and
    the book.

    Relationships:
        user (User):
            Many-to-one relationship with the `User` model, indicating the user who has marked the book as "to-read".

        book (Book):
            Many-to-one relationship with the `Book` model, indicating the book that the user wants to read.
    """
    id = db.Column(db.Integer, primary_key=True)
    toread = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class Review(db.Model):
    """
    Review model representing a user's review of a book.

    This model stores the review text provided by a user for a specific book and links to both the user and the book.

    Relationships:
        user (User):
            Many-to-one relationship with the `User` model, indicating the user who wrote the review.

        book (Book):
            Many-to-one relationship with the `Book` model, indicating the book that is being reviewed.
    """
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String(1000), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)


class AdminModelView(ModelView):
    """
    Custom ModelView for administrative access control in Flask-Admin.

    This view overrides the default `is_accessible` method to restrict access to only users with administrative
    privileges.
    Specifically, it checks if the current user is authenticated and has the username "Admin".

    Methods:
        is_accessible():
            Checks if the current user has administrative access.
            Returns True if the user is authenticated and their name is "Admin", otherwise False.
            Displays a flash message if access is denied.
    """
    def is_accessible(self):
        is_admin = current_user.is_authenticated and current_user.name == "Admin"
        if not is_admin:
            flash("You dont have permits to access this page!", "error")
        return is_admin
