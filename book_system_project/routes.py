from flask import Flask, render_template, redirect, request, url_for, flash, session
from book_system_project import db, app, login_manager, bcrypt
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


@app.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template("profile.html", user=user)


@app.route("/fill_db", methods=["GET", "POST"])
def fill_db():
    books_added = 0
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
                books_added += 1
            except IntegrityError:
                db.session.rollback()
                continue

        if books_added == 0:
            flash('Books you are trying to add already exists. No new books added!', 'info')
        else:
            flash(f'Successfully added {books_added} new book(s) to the database!', 'success')
    return render_template("fill_db.html", message="Database filled successfully.")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        phone = form.phone.data
        date_of_birth = form.date_of_birth.data
        print(date_of_birth)
        gender = form.gender.data
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            flash('User with this email already exists', 'error')
            return render_template('register.html', form=form)
        if password != confirm_password:
            flash('Passwords, do not match!', 'error')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, name=name, password=hashed_password, phone=phone, date_of_birth=date_of_birth,
                        gender=gender)

        db.session.add(new_user)
        db.session.commit()
        flash(f'You have succesfully registered, {name}! Login now.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(' You have logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('home'))


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        author = form.name.data
        check_author = Author.query.filter_by(name=author).first()
        if check_author:
            flash('This author already exists.', 'error')
            return render_template('add_author.html', form=form)
        new_author = Author(name=author)
        db.session.add(new_author)
        db.session.commit()
        flash('You have successfully added new author.', 'success')
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

        existing_book = Book.query.filter_by(title=title, author_id=author_id).first()
        if existing_book:
            flash('This book already exists.', 'error')
            return render_template('add_book.html', form=form)

        all_genres = request.form.getlist('genre')
        if not all_genres:
            flash('Please select at least one genre.', 'error')
            return render_template('add_book.html', form=form)

        new_book = Book(title=title, author_id=author_id)
        for genre_id in all_genres:
            genre = Genre.query.get(int(genre_id))
            if genre:
                new_book.genres.append(genre)
        db.session.add(new_book)
        db.session.commit()
        flash('You have successfully added new book', 'success')
        return redirect(url_for('add_book'))
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
