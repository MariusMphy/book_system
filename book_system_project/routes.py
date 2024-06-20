from flask import Flask, render_template, redirect, request, url_for, flash, session
from book_system_project import db, app, login_manager
from book_system_project.models import Book, User, Rating, Author, Genre
from book_system_project.forms import RegisterForm, LoginForm, BookForm
from flask_login import login_user, login_required, logout_user, current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/fill_db", methods=["GET", "POST"])
def fill_db():
    pass


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


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    form = BookForm()
    form.author.choices = [(author.id, author.name) for author in Author.query.all()]
    form.genre.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

    if form.validate_on_submit():
        title = form.title.data
        author_id = form.author.data
        genre_id = form.genre.data

        new_book = Book(title=title, author_id=author_id, genre_id=genre_id)
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
    genre = book.genre
    return render_template('book.html', book=book, author=author, genre=genre)
