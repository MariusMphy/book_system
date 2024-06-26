from flask import Flask, render_template, redirect, request, url_for, flash, session
from book_system_project import db, app, login_manager
from book_system_project.models import Book, User, Rating, Author, Genre
from book_system_project.forms import RegisterForm, LoginForm, BookForm, AuthorForm
from flask_login import login_user, login_required, logout_user, current_user
import csv
from sqlalchemy.exc import IntegrityError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/fill_db", methods=["GET", "POST"])
def fill_db():
    with open('book_system_project/media/top20_books.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            author_name = row['Author'].strip()
            book_title = row['Title'].strip()
            genre_names = [genre.strip() for genre in row['Genres'].split(',')]

            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.commit()

            genres = []
            for genre_name in genre_names:
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                    db.session.commit()
                genres.append(genre)

            existing_book = Book.query.filter_by(title=book_title, author_id=author.id).first()
            if existing_book:
                continue

            book = Book(title=book_title, author_id=author.id)
            for genre in genres:
                book.genres.append(genre)

            db.session.add(book)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

    return render_template("fill_db.html", message="Database filled successfully.")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        user = User.query.filter_by(name=name).first()
        login_user(user)
        return redirect(url_for("home"))
    return render_template("login.html", form=form, user=current_user)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        author = form.name.data
        new_author = Author(name=author)
        db.session.add(new_author)
        db.session.commit()
        return render_template('add_author.html', form=form)
    return render_template('add_author.html', form=form)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    form = BookForm()
    form.author.choices = [(author.id, author.name) for author in Author.query.all()]
    form.genre.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

    if form.validate_on_submit():
        title = form.title.data
        author_id = form.author.data
        all_genres = request.form.getlist('genre')

        if not all_genres:
            return render_template('add_book.html', form=form, error='Please select at least one genre.')

        new_book = Book(title=title, author_id=author_id)
        for genre_id in all_genres:
            genre = Genre.query.get(int(genre_id))
            if genre:
                new_book.genres.append(genre)

        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_book.html', form=form)


@app.route("/view_books", methods=["GET", "POST"])
def view_books():
    books = Book.query.all()
    return render_template("view_books.html", books=books)


@app.route("/book/<int:book_id>")
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    genres = book.genres
    return render_template('book.html', book=book, author=author, genres=genres)

