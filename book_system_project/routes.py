from flask import Response, render_template, redirect, request, url_for, flash
from book_system_project import login_manager, bcrypt, logger
from book_system_project.models import db, Book, User, Rating, Author, Genre, ToRead, Review, book_genres
from book_system_project.forms import (RegisterForm, LoginForm, BookForm, AuthorForm, RateBook, EditUserForm,
                                       ChangePasswordForm, SortRating, ToReadForm, WriteReviewForm, SearchForm)
from flask_login import login_user, login_required, logout_user, current_user
import csv
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime
from random import randint, choice
from book_system_project.media.books66 import books_list
from flask_paginate import Pagination, get_page_parameter
import json
import os
import uuid
from book_system_project.blueprints import bp
from typing import List, Tuple


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Load a user by their user ID.

    This function is used by Flask-Login to retrieve the current logged-in user
    from the database.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user object corresponding to the given user ID, or None if no user
        is found.
    """
    user = User.query.get(int(user_id))
    return user


@bp.route("/")
def home() -> Response:
    """
    Render the home page with top books in various categories.

    This function queries all books from the database and calculates the top 5 books
    based on average rating, the number of reviews, and the number of times added to
    the read list. It then renders the 'base.html' template with these top books.

    Returns:
        A rendered HTML template 'base.html' with the following context variables:
        - top5_books: A list of tuples containing the top 5 books by average rating
                      and their respective ratings.
        - top_reviewed_books: A list of tuples containing the top 5 books by review count
                              and their respective review counts.
        - top_read_listed_books: A list of tuples containing the top 5 books by read list
                                 count and their respective read list counts.
    """
    books = Book.query.all()
    books_with_avg_rating = [(book, book.avg_rating) for book in books if book.avg_rating is not None]
    top5_books = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)[:5]

    books_with_review_count = [(book, len(Review.query.filter_by(book_id=book.id).all())) for book in books]
    top_reviewed_books = sorted(books_with_review_count, key=lambda x: x[1], reverse=True)[:5]

    books_with_read_list_count = [(book, len(ToRead.query.filter_by(book_id=book.id).all())) for book in books]
    top_read_listed_books = sorted(books_with_read_list_count, key=lambda x: x[1], reverse=True)[:5]

    return render_template("base.html", top5_books=top5_books, top_reviewed_books=top_reviewed_books,
                           top_read_listed_books=top_read_listed_books)


@bp.route("/profile")
@login_required
def profile() -> Response:
    """
    Render the profile page for the logged-in user.

    This function requires the user to be logged in. It retrieves the current user
    and renders the 'profile.html' template with the user information.

    Returns:
        Response: A rendered HTML template 'profile.html' with the current user context.
    """
    user = current_user
    return render_template("profile.html", user=user)


@bp.route("/fill_db")
@login_required
def fill_db() -> Response:
    """
    Render the fill_db page for the Admin user.

    This function checks if the logged-in user is the Admin. If not, it logs a warning,
    flashes an error message to the user, and redirects to the home page. If the user
    is the Admin, it renders the 'fill_db.html' template.

    Returns:
        Response: A rendered HTML template 'fill_db.html' if the user is Admin,
                  otherwise a redirection to the home page with a flash message.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /fill_db by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    return render_template('fill_db.html')


@bp.route("/fill_book_db", methods=["GET", "POST"])
@login_required
def fill_book_db() -> Response:
    """
    Handle the process of filling the book database with new entries.

    This function is accessible only to the Admin user. It iterates through a predefined
    list of books, checks if the author and genres exist in the database, and adds them
    if they do not. It then adds the book to the database if it does not already exist.

    Returns:
        Response: A rendered HTML template 'fill_db.html' if the user is Admin,
                  otherwise a redirection to the home page with a flash message.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /fill_book_db by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    books_added = 0
    for book in books_list:
        author_name = book['Author']
        book_title = book['Title']
        genre_names = book['Genres'].split(',')

        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        genres = []
        for genre_name in genre_names:
            genre = Genre.query.filter_by(name=genre_name.strip()).first()
            if not genre:
                genre = Genre(name=genre_name.strip())
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
        flash('Books you are trying to add already exists. No new books added.', 'info')
    else:
        flash(f'Successfully added {books_added} new book(s) to the database!', 'success')
    return render_template("fill_db.html")


@bp.route("/fill_user_db", methods=["GET", "POST"])
@login_required
def fill_user_db() -> Response:
    """
    Handle the process of filling the user database with new entries.

    This function is accessible only to the Admin user. It checks if the number of
    users in the database exceeds 50. If not, it reads user data from a specified
    file and attempts to add each user to the database.

    Returns:
        Response: A rendered HTML template 'fill_db.html' if the users are added,
                  or 'admin_page.html' if the user count exceeds 50, otherwise a
                  redirection to the home page with a flash message.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /fill_user_db by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    if len(User.query.all()) > 50:
        flash("We have enough users already. No new users added.", 'info')
        return render_template("admin_page.html")
    users_added = 0
    with open('book_system_project/media/users60.txt', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            full_name = f"{row['first_name'].strip()} {row['last_name'].strip()}"

            user = User(
                name=full_name,
                email=row['email'],
                password=bcrypt.generate_password_hash(row['password']).decode('utf-8'),
                phone=row['phone'],
                date_of_birth=datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(),
                gender=row['gender']
            )
            db.session.add(user)
            try:
                db.session.commit()
                users_added += 1
            except IntegrityError:
                db.session.rollback()
                continue

        if users_added == 0:
            flash('Users you are trying to add already exists. No new users added.', 'info')
        else:
            flash(f'Successfully added {users_added} new user(s) to the database!', 'success')

    return render_template("fill_db.html")


def randomize_review() -> str:
    """
    Generate a random review composed of a series of sentences.

    This function reads a file containing a list of words, splits them into a list,
    and generates a random review by forming sentences of random lengths from these words.

    Returns:
        str: A randomly generated review consisting of 5 to 12 sentences.
    """
    with open('book_system_project/media/words3000.txt', 'r') as file:
        words = file.read()
    words = words.split()

    def get_result(word_list, sentence_length) -> str:
        """
        Generate a random sentence from a list of words.

        Args:
            word_list (list): The list of words to form sentences from.
            sentence_length (int): The number of words in the sentence.

        Returns:
            str: A randomly generated sentence with the specified length.
        """
        sentence = ' '.join(choice(word_list) for _ in range(sentence_length))
        return sentence[0].upper() + sentence[1:]

    number_of_sentences = randint(5, 12)
    sentences = [get_result(words, randint(5, 15)) for _ in range(number_of_sentences)]
    return '. '.join(sentences) + '.'


@bp.route("/fill_ratings", methods=["GET", "POST"])
@login_required
def fill_ratings() -> Response:
    """
    Populate the database with random ratings, read lists, and reviews.

    This function is accessible only to the Admin user. It checks if the number of ratings
    in the database exceeds 50. If not, it generates random ratings and reviews for each
    user (excluding the current user), and updates the 'ToRead' list. The amount and type
    of data generated are influenced by the position of the counter in a defined range.

    Returns:
        Response: A rendered HTML template 'fill_db.html' if the data is updated successfully,
                  or 'admin_page.html' if there is enough data already, or redirects to the
                  home page with a flash message if the user is not an Admin.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /fill_ratings by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    user_rate = User.query.all()
    if len(Rating.query.all()) > 50:
        flash("We have enough data already. No new data added.", 'info')
        return render_template("admin_page.html")
    for user in user_rate:
        if user.id != current_user.id:
            book_list = Book.query.all()
            to_rate = int(len(book_list) * 0.9)
            counter = 0
            for book in book_list:
                check = Rating.query.filter_by(user_id=user.id, book_id=book.id).first()
                if check:
                    continue
                if counter < to_rate:
                    review = randomize_review()
                    rating = randint(1, 5)
                    if counter <= 30:
                        add_rating = Rating(user_id=user.id, rating=rating, book_id=book.id)
                        db.session.add(add_rating)
                    if 30 < counter <= 40:
                        add_rating = Rating(user_id=user.id, rating=randint(4, 5), book_id=book.id)
                        db.session.add(add_rating)
                    if 40 < counter <= 50:
                        add_rating = Rating(user_id=user.id, rating=randint(1, 2), book_id=book.id)
                        db.session.add(add_rating)
                    if 10 < counter <= 50 and randint(1, 3) > 1:
                        add_to_read = ToRead(user_id=user.id, toread=1, book_id=book.id)
                        db.session.add(add_to_read)
                    if 20 < counter <= 60 and randint(1, 3) > 1:
                        add_review = Review(user_id=user.id, review=review, book_id=book.id)
                        db.session.add(add_review)
                    counter += 1
            db.session.commit()
    flash("Ratings, read list and reviews have been updated", 'success')
    return render_template("fill_db.html")


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response:
    """
    Handle user registration for new accounts.

    This function processes both GET and POST requests for user registration. On a POST request,
    it validates the registration form, checks if the provided email is already in use, and
    ensures that the passwords match. If the checks pass, it creates a new user record in the database.

    Returns:
        Response: Renders the 'register.html' template with the registration form if there are validation errors,
                  or redirects to the login page upon successful registration.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        phone = form.phone.data
        date_of_birth = form.date_of_birth.data
        gender = form.gender.data
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            logger.warning(f"Trying to register with existing email: {check_email.email}")
            flash('User with this email already exists.', 'error')
            return render_template('register.html', form=form)
        if password != confirm_password:
            flash('Passwords, do not match!', 'error')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, name=name, password=hashed_password, phone=phone, date_of_birth=date_of_birth,
                        gender=gender)

        db.session.add(new_user)
        db.session.commit()
        logger.info(f"Successfully registered user_id: {new_user.id} email: {new_user.email}")
        flash(f'You have successfully registered, {name}!', 'success')
        return redirect(url_for('main.login'))
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response:
    """
    Handle user login functionality.

    This function processes both GET and POST requests for user login. On a POST request,
    it validates the login form, checks if the provided email exists in the database, and
    verifies the password. If the credentials are correct, it logs in the user and redirects
    to the user's profile page. If the credentials are incorrect, it provides feedback and
    re-renders the login form.

    Returns:
        Response: Renders the 'login.html' template with the login form if the form is invalid or
                  the login fails, or redirects to the profile page upon successful login.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"Logged in user_id: {user.id}, email: {user.email}")
            flash(' You have logged in successfully!', 'success')
            return redirect(url_for('main.profile'))
        else:
            logger.warning(f"Failed to login with email: {email}")
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form, user=current_user)


@bp.route('/logout')
@login_required
def logout() -> Response:
    """
    Handle user logout functionality.

    This function logs out the current user, provides feedback via a flash message, and
    redirects the user to the home page. It requires that the user be logged in to access
    the logout functionality.

    Returns:
        Response: Redirects to the home page after logging out the user, with a flash message
                  indicating a successful logout.
    """
    logger.info(f"Logged out user_id: {current_user.id}, email: {current_user.email}")
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('main.home'))


@bp.route("/add_author", methods=["GET", "POST"])
@login_required
def add_author() -> Response:
    """
    Handle the addition of a new author to the database.

    This function allows an admin user to add a new author through a form. It checks if the
    current user is an admin before proceeding. Upon receiving a valid form submission, it
    verifies if the author already exists in the database. If not, it adds the new author
    to the database and provides feedback to the user.

    Returns:
        Response: Renders the 'add_author.html' template with the form, either showing
                  a success message if the author was added, or an error message if the
                  author already exists. If the user is not an admin, redirects to the home page.
    """
    if current_user.name != "Admin":
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
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
        logger.info(f"User_id: {current_user.id}, added new author: {new_author.name}")
        flash('You have successfully added new author.', 'success')
        return render_template('add_author.html', form=form)
    return render_template('add_author.html', form=form)


@bp.route("/view_users", methods=["GET"])
@login_required
def view_users() -> Response:
    """
    Display a paginated list of users for admin view.

    This function allows an admin user to view a paginated list of all users. It ensures that
    only admin users can access this page. The function retrieves user data, paginates the results,
    and renders the `view_users.html` template with the list of users. If the user is not an admin,
    they are redirected to the home page with an error message.

    Returns:
        Response: Renders the 'view_users.html' template with the list of users and pagination
                  controls if the user has admin privileges. If no users are found or if the user
                  is not an admin, it renders the 'admin_page.html' template or redirects to the
                  home page.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /view_users by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    users_query = User.query
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    users_pagination = users_query.paginate(page=page, per_page=per_page)
    users = users_pagination.items
    total = users_pagination.total
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = (page - 1) * per_page + 1
    if users:
        return render_template('view_users.html', users=users, pagination=pagination, start_num=start_num)
    return render_template('admin_page.html')


@bp.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book() -> Response:
    """
    Handle the addition of a new book to the database.

    This function allows an admin user to add a new book through a form. It verifies that the
    current user is an admin before processing the request. It populates the form with available
    authors and genres, validates the form submission, checks for existing books with the same title
    and author, and adds the new book to the database. It also handles genre selections and provides
    feedback to the user.

    Returns:
        Response: Renders the 'add_book.html' template with the form. If the book is successfully
                  added, the user is redirected to the same page with a success message. If the
                  book already exists or if form validation fails, the template is rendered with
                  appropriate error messages.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /add_book by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
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
        return redirect(url_for('main.add_book'))
    return render_template('add_book.html', form=form)


@bp.route("/view_books", methods=["GET"])
def view_books() -> Response:
    """
    Display a list of all books in the database.

    This function retrieves all books from the database and renders the `view_books.html`
    template to display them. It does not require user authentication.

    Returns:
        Response: Renders the 'view_books.html' template with a list of all books.
    """
    books_query = Book.query

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    books_pagination = books_query.paginate(page=page, per_page=per_page)
    books = books_pagination.items
    total = books_pagination.total
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = (page - 1) * per_page + 1


    return render_template("view_books.html", books=books, pagination=pagination, start_num=start_num)


@bp.route("/book/<int:book_id>", methods=["GET", "POST"])
def book_details(book_id: int) -> Response:
    """
     Display details of a specific book, including author, genres, ratings, and reviews.

     This function handles both GET and POST requests. For GET requests, it retrieves the book details
     including the author, genres, average rating, user-specific rating, and reviews. For authenticated
     users, it checks if the book is already in their "to-read" list and handles adding/removing the book
     from this list via form submission.

     Parameters:
         book_id (int): The ID of the book whose details are to be displayed.

     Returns:
         Response: Renders the 'book.html' template with the book details, including author, genres,
                   average rating, user-specific rating, and review information. If the form is submitted,
                   it processes the addition of the book to the user's "to-read" list and provides feedback.
     """
    form = ToReadForm()
    book = Book.query.get_or_404(book_id)
    author = book.author
    genres = book.genres
    review_count = len(Review.query.filter_by(book_id=book_id).all())
    review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first() \
        if current_user.is_authenticated else None
    avg_rating = book.avg_rating
    rating = None

    if current_user.is_authenticated:
        rating = Rating.query.filter_by(book_id=book_id, user_id=current_user.id).first()

    if form.validate_on_submit():
        existing_toread = ToRead.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if not existing_toread:
            new_toread = ToRead(toread=True, user_id=current_user.id, book_id=book_id)
            db.session.add(new_toread)
            db.session.commit()
            flash('You have successfully added this book to your read list', 'success')
            return redirect(url_for('main.to_read'))
        flash('This book is already in your read list', 'error')
        return redirect(url_for('main.to_read'))

    toread = ToRead.query.filter_by(user_id=current_user.id, book_id=book_id).first() \
        if current_user.is_authenticated else None
    read_listed = len(ToRead.query.filter_by(book_id=book_id).all())
    return render_template('book.html', form=form, book=book, author=author, genres=genres, avg_rating=avg_rating,
                           rating=rating, toread=toread, review=review, review_count=review_count,
                           read_listed=read_listed)


@bp.route("/rate_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def rate_book(book_id: int) -> Response:
    """
    Allow authenticated users to rate a specific book.

    This function handles both GET and POST requests. For GET requests, it retrieves the details of
    the book, including its author, genres, and average rating. For authenticated users, it also
    fetches their current rating (if any). For POST requests, it processes the submitted rating and
    updates or creates a new rating entry in the database.

    Parameters:
        book_id (int): The ID of the book to be rated.

    Returns:
        Response: Renders the 'rate_book.html' template with the book details, average rating, current
                  rating, and a form for submitting a new rating. If the form is submitted, updates the
                  rating in the database and provides feedback.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author
    genres = book.genres
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else "Not rated"
    current_rating = Rating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    form = RateBook(rating=current_rating.rating if current_rating else None)

    if form.validate_on_submit():
        rating = form.rating.data
        if current_rating:
            current_rating.rating = rating
        else:
            new_rating = Rating(rating=rating, book_id=book_id, user_id=current_user.id)
            db.session.add(new_rating)
        db.session.commit()
        logger.info(f"User_id: {current_user.id}, rated book_id: {book_id}, book_name: {book.title}")
        flash('Thank you for your rating!', 'success')
        return redirect(url_for('main.book_details', book_id=book_id))
    return render_template('rate_book.html', book=book, author=author, genres=genres, avg_rating=avg_rating,
                           current_rating=current_rating, form=form)


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Response:
    """
    Allow authenticated users to update their profile information.

    This function handles both GET and POST requests. For GET requests, it displays the user's current
    profile information in a form. For POST requests, it validates the submitted form data, checks the
    user's password for security, updates the user's profile information (name, phone, date of birth,
    and gender) if the password is correct, and saves the changes to the database. It also provides feedback
    to the user about the success or failure of the profile update.

    Returns:
        Response: Renders the 'edit_profile.html' template with the current profile information and a form
                  for updating the profile. On form submission, it updates the user's profile and provides
                  appropriate feedback.
    """
    form = EditUserForm()
    current_email = current_user.email
    current_name = current_user.name
    current_phone = current_user.phone
    current_date_of_birth = current_user.date_of_birth
    current_gender = current_user.gender

    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            if form.name.data:
                current_user.name = form.name.data
            if form.phone.data:
                current_user.phone = form.phone.data
            if form.date_of_birth.data:
                current_user.date_of_birth = form.date_of_birth.data
            if form.gender.data:
                current_user.gender = form.gender.data
            db.session.commit()
            logger.info(f"User_id: {current_user.id} updated profile")
            flash("Profile updated successfully", "success")
        else:
            logger.warning(f"User_id: {current_user.id} failed password, while updating profile")
            flash("Password is incorrect", "error")
            return redirect(url_for('main.edit_profile'))
    return render_template("edit_profile.html", form=form, current_email=current_email, current_name=current_name,
                           current_phone=current_phone, current_date_of_birth=current_date_of_birth,
                           current_gender=current_gender)


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password() -> Response:
    """
    Handle the password change request for the authenticated user.

    This function processes both GET and POST requests. For GET requests, it renders a form for the user
    to input their old password, new password, and confirm the new password. For POST requests, it validates
    the form data, checks if the old password is correct, verifies that the new password and its confirmation
    match, updates the user's password if all checks pass, and saves the changes to the database. It also
    provides feedback to the user about the success or failure of the password update process.

    Returns:
        Response: Renders the 'change_password.html' template with a form for changing the password. On
                  successful password change, redirects the user to the home page with a success message.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if not bcrypt.check_password_hash(current_user.password, old_password):
            logger.warning(f"User_id: {current_user.id} failed old password, while updating password")
            flash("Old password is incorrect", "error")
            return render_template('change_password.html', form=form)
        if new_password != confirm_password:
            logger.warning(f"User_id: {current_user.id} failed to confirm new password, while updating password")
            flash('Passwords, do not match!', 'error')
            return render_template('change_password.html', form=form)
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        logger.info(f"User_id: {current_user.id} changed password")
        flash(f'Password is updated', 'success')
        return redirect(url_for('main.home'))
    return render_template('change_password.html', form=form)


@bp.route("/your_ratings", methods=["GET", "POST"])
@login_required
def your_ratings() -> Response:
    """
    Display and sort the ratings given by the current user for books.

    This function handles both GET and POST requests. For GET requests, it retrieves all ratings given by the
    current user and displays them along with the corresponding books. For POST requests, it sorts the ratings
    based on the user's selection and updates the display accordingly.

    The function performs the following tasks:
    - Retrieves all ratings given by the current user and their associated books.
    - Formats the ratings and books into a list of dictionaries.
    - Sorts the list based on the user's selection if a POST request is made.
      The sorting options include:
        - "best": Sort by rating value in descending order.
        - "worst": Sort by rating value in ascending order.
        - "newest": Sort by the rating ID (newest first).
        - "oldest": Sort by the rating ID (oldest first).

    Returns:
        Response: Renders the 'your_ratings.html' template with the sorted list of rated books and the form used for
        sorting.
    """
    form = SortRating()
    ratings_with_books = db.session.query(Rating, Book).join(Book).filter(Rating.user_id == current_user.id).all()
    rated_books = [{'book': book, 'rating': rating.rating, 'rating_id': rating.id} for rating, book in
                   ratings_with_books]

    sorted_books_query = sorted(rated_books, key=lambda x: x['rating'], reverse=True)
    if request.method == 'POST' and form.validate_on_submit():
        sorting = form.sorted.data
        if sorting == "best":
            sorted_books_query = sorted(rated_books, key=lambda x: x['rating'], reverse=True)
        elif sorting == "worst":
            sorted_books_query = sorted(rated_books, key=lambda x: x['rating'], reverse=False)
        elif sorting == "newest":
            sorted_books_query = sorted(rated_books, key=lambda x: x['rating_id'], reverse=True)
        elif sorting == "oldest":
            sorted_books_query = sorted(rated_books, key=lambda x: x['rating_id'], reverse=False)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total = len(sorted_books_query)
    start = (page - 1) * per_page
    end = start + per_page
    sorted_books = sorted_books_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("your_ratings.html", form=form, sorted_books=sorted_books,
                           ratings_with_books=ratings_with_books, pagination=pagination, start_num=start_num)


@bp.route("/to_read", methods=["GET"])
@login_required
def to_read() -> Response:
    """
    Display the list of books that the current user has marked to read.

    This function handles GET requests and retrieves the list of books that the current user has marked to read.
    It joins the `ToRead` and `Book` tables to get the relevant book information for the current user.

    The function performs the following tasks:
    - Retrieves all `ToRead` entries for the current user and the associated `Book` records.
    - Formats the retrieved data into a list of dictionaries where each dictionary contains:
        - `book`: The book object.
        - `toread`: The `ToRead` entry associated with the book.
    - Renders the `to_read.html` template with the formatted list of books.

    Returns:
        Response: An HTTP response object that renders the 'to_read.html' template with the list of books marked
                  to read by the current user.
    """
    toread_list = db.session.query(ToRead, Book).join(Book).filter(ToRead.user_id == current_user.id).all()
    books_query = [{'book': book, 'toread': toread} for toread, book in toread_list]

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total = len(books_query)
    start = (page - 1) * per_page
    end = start + per_page
    books = books_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("to_read.html", books=books, pagination=pagination, start_num=start_num)


@bp.route("/remove_to_read/<int:book_id>", methods=["GET", "POST"])
@login_required
def remove_to_read(book_id: int) -> Response:
    """
    Remove a book from the user's "to read" list.

    This function handles GET and POST requests to remove a specified book from the current user's "to read" list.
    It first retrieves the `ToRead` entry for the specified book and current user. If found, it deletes the entry
    from the database and commits the change. If the entry is not found, it flashes an error message.

    The function performs the following tasks:
    - Retrieves the `ToRead` entry for the specified `book_id` and the current user.
    - Deletes the entry from the database if it exists and commits the changes.
    - Logs the removal action and flashes a success message if the book was removed.
    - Flashes an error message if the book was not found in the user's read list.
    - Redirects the user to the "to read" page.

    Parameters:
        book_id (int): The ID of the book to be removed from the "to read" list.

    Returns:
        Response: An HTTP response object that performs a redirection to the 'to_read' page.
    """
    toread_to_remove = ToRead.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if toread_to_remove:
        db.session.delete(toread_to_remove)
        db.session.commit()
        logger.info(f"User_id: {current_user.id}, removed book_id {book_id} from read list")
        flash('Book has been removed from your read list', 'success')
    else:
        flash('Book not found in your read list', 'error')
    return redirect(url_for('main.to_read'))


@bp.route("/write_review/<int:book_id>", methods=["GET", "POST"])
@login_required
def write_review(book_id: int) -> Response:
    """
    Allow the user to write or update a review for a specific book.

    This function handles GET and POST requests for writing or updating a review for a book identified by `book_id`.
    It retrieves the existing review by the current user for the specified book, if any. If a review already exists,
    it updates it; otherwise, it creates a new review. The function also retrieves the book details and author name to
    display in the review form.

    The function performs the following tasks:
    - Retrieves the existing review for the specified book and user, if it exists.
    - Retrieves the book details and author name.
    - If the form is validated on submission, it updates or creates a review.
    - Commits the changes to the database and logs the review action.
    - Flashes a success message and redirects the user to the book details page upon successful review submission.
    - Renders the review form with existing review data and book details if the form is not submitted or invalid.

    Parameters:
        book_id (int): The ID of the book for which the review is being written or updated.

    Returns:
        Response: An HTTP response object that either renders the review form or performs a redirection to the book details page.
    """
    form = WriteReviewForm()
    old_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    book = Book.query.filter_by(id=book_id).first()
    author = db.session.query(Author.name).join(Book, Book.author_id == Author.id).filter(Book.id == book_id).scalar()
    if form.validate_on_submit():
        review = form.review.data
        if old_review:
            old_review.review = review
        else:
            new_review = Review(review=review, book_id=book_id, user_id=current_user.id)
            db.session.add(new_review)
        db.session.commit()
        logger.info(f"User_id: {current_user.id}, wrote review for book_id: {book_id}")
        flash('Thank you for your review!', 'success')
        return redirect(url_for('main.book_details', book_id=book_id))
    return render_template('write_review.html', form=form, review=old_review, book=book, author=author)


@bp.route("/your_reviews", methods=["GET"])
@login_required
def your_reviews() -> Response:
    """
    Retrieve and display all reviews written by the current user.

    This function queries the database to retrieve all reviews written by the currently logged-in user. It gathers
    details such as the review text, book title, book ID, author name, and username. The retrieved data is then
    formatted and passed to the `your_reviews.html` template for rendering.

    The function performs the following tasks:
    - Queries the `Review`, `Book`, `Author`, and `User` tables to retrieve relevant review information for the
      current user.
    - Formats the retrieved data into a list of dictionaries containing review details.
    - Renders the `your_reviews.html` template, passing the formatted review information.

    Returns:
        Response: An HTTP response object that renders the `your_reviews.html` template with the current user's review
        information.
    """
    reviews = db.session.query(
        Review.review,
        Book.title,
        Book.id.label('book_id'),
        Author.name.label('author_name'),
        User.name.label('user_name')
    ).join(Book, Review.book_id == Book.id) \
        .join(Author, Book.author_id == Author.id) \
        .join(User, Review.user_id == User.id) \
        .filter(User.id == current_user.id).all()

    rev_info_query = [
        {
            "review": review.review,
            "book_title": review.title,
            "book_id": review.book_id,
            "author_name": review.author_name,
            "user_name": review.user_name,

        }
        for review in reviews
    ]

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    total = len(rev_info_query)
    start = (page - 1) * per_page
    end = start + per_page
    rev_info = rev_info_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template('your_reviews.html', rev_info=rev_info, pagination=pagination, start_num=start_num)


@bp.route("/book_reviews/<int:book_id>", methods=["GET", "POST"])
def book_reviews(book_id: int) -> Response:
    """
    Display and sort reviews for a specific book.

    This function handles both GET and POST requests to display reviews for a specific book. It retrieves the book
    details, including the book's author and associated reviews. Reviews are optionally sorted based on user input
    through a form.

    On GET requests, the function retrieves all reviews for the specified book, including associated usernames and
    ratings. Reviews are initially sorted by their ID in descending order. On POST requests, it processes sorting
    criteria from the form and re-sorts the reviews accordingly.

    Parameters:
        book_id (int): The ID of the book for which reviews are being displayed.

    Returns:
        Response: An HTTP response object that renders the `book_reviews.html` template with the book details, author,
                  and sorted review information.
    """
    form = SortRating()
    book = Book.query.filter_by(id=book_id).first()
    author = Author.query.filter_by(id=book.author_id).first()

    reviews = (db.session.query(Review.review, Review.id, User.name, Rating.rating)
               .join(User, Review.user_id == User.id)
               .outerjoin(Rating, (Rating.user_id == User.id) & (Rating.book_id == book_id))
               .filter(Review.book_id == book_id).all())

    rev_info = [
        {
            "review": review.review,
            "name": review.name,
            "rating": review.rating,
            "rating_id": review.id
        }
        for review in reviews
    ]

    sorted_rev_info_query = sorted(rev_info, key=lambda x: x['rating_id'], reverse=True)
    if request.method == 'POST' and form.validate_on_submit():
        sorting = form.sorted.data
        if sorting == "best":
            sorted_rev_info_query = sorted(rev_info, key=lambda x: x['rating'], reverse=True)
        elif sorting == "worst":
            sorted_rev_info_query = sorted(rev_info, key=lambda x: x['rating'], reverse=False)
        elif sorting == "newest":
            sorted_rev_info_query = sorted(rev_info, key=lambda x: x['rating_id'], reverse=True)
        elif sorting == "oldest":
            sorted_rev_info_query = sorted(rev_info, key=lambda x: x['rating_id'], reverse=False)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    total = len(sorted_rev_info_query)
    start = (page - 1) * per_page
    end = start + per_page
    sorted_rev_info = sorted_rev_info_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template('book_reviews.html', form=form, rev_info=sorted_rev_info, book=book,
                           author=author, pagination=pagination, start_num=start_num)


@bp.route("/admin_page", methods=["GET"])
@login_required
def admin_page() -> Response:
    """
    Render the admin page if the current user is an admin.

    This function is accessible only to users with the name "Admin". It verifies if the currently logged-in user
    has the admin role. If the user is not an admin, it logs a warning message, flashes an error message, and
    redirects the user to the home page. If the user is an admin, it logs an info message and renders the admin
    page template.

    Returns:
        Response: An HTTP response object that renders the `admin_page.html` template if the user is an admin,
                  otherwise redirects to the home page with an error message.
    """
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /admin_page by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    logger.info(f"Admin_page accessed by admin: {current_user.id}")
    return render_template('admin_page.html')


@bp.route("/search", methods=["GET", "POST"])
def search() -> Response:
    """
    Handle search requests for books based on various criteria.

    This function processes search requests from the user, allowing searches based on book title, author, genre,
    rating range, and review presence. It also provides sorting options for the search results.

    On GET requests, it initializes the search form with available authors and genres.

    On POST requests, it performs the search based on the submitted form data, filtering and sorting the results
    according to user inputs. It also saves the search results in a JSON file if the user is authenticated.

    The search results are either displayed to the user or a message is flashed if no results are found.

    Returns:
        Response: An HTTP response object that renders the `search.html` template with the search form, results,
                  count of results, and any saved searches.
    """
    form = SearchForm()
    form.select_author.choices = [('', 'Select an author')] + [(author.name, author.name) for author in
                                                               Author.query.order_by(Author.name).all()]
    form.select_genre.choices = [('', 'Select genre')] + [(genre.name, genre.name) for genre in
                                                          Genre.query.order_by(Genre.name).all()]
    results = []

    saved_searches = []
    if os.path.exists('instance/search_results.json'):
        with open('instance/search_results.json', 'r') as file:
            saved_searches = json.load(file)

    if form.validate_on_submit():
        title = form.title.data
        author = form.select_author.data or form.author.data
        genre = form.select_genre.data or form.genre.data
        rating_min = form.rating_min.data
        rating_max = form.rating_max.data
        sort_by = form.sort_by.data

        book_alias = db.aliased(Book)
        rating_alias = db.aliased(Rating)
        query = db.session.query(book_alias).join(Author)

        if title:
            query = query.filter(book_alias.title.ilike(f'%{title}%'))
        if author:
            query = query.filter(Author.name.ilike(f'%{author}%'))

        if genre:
            query = query.join(book_genres, book_alias.id == book_genres.c.book_id) \
                .join(Genre, Genre.id == book_genres.c.genre_id) \
                .filter(Genre.name.ilike(f'%{genre}%'))

        if rating_min or rating_max:
            query = query.join(rating_alias, book_alias.id == rating_alias.book_id).group_by(book_alias.id)
            if rating_min:
                query = query.having(func.avg(rating_alias.rating) >= int(rating_min))
            if rating_max:
                query = query.having(func.avg(rating_alias.rating) <= int(rating_max))
        if form.review.data:
            query = query.filter(book_alias.reviews.any())

        if sort_by == 'rating_asc':
            query = query.outerjoin(Rating, book_alias.id == Rating.book_id) \
                .group_by(book_alias.id) \
                .order_by(func.avg(Rating.rating).asc())
        elif sort_by == 'rating_desc':
            query = query.outerjoin(Rating, book_alias.id == Rating.book_id) \
                .group_by(book_alias.id) \
                .order_by(func.avg(Rating.rating).desc())

        results = query.all()

        if current_user.is_authenticated:
            serialized_results = []
            for result in results:
                serialized_results.append({
                    'id': result.id,
                    'title': result.title,
                    'author': {'name': result.author.name},
                    'genres': [{'name': genre.name} for genre in result.genres],
                    'avg_rating': result.avg_rating
                })
            current_time = datetime.now().isoformat()
            search_id = str(uuid.uuid4())

            timed_results = {
                "search_id": search_id,
                "user_id": current_user.id,
                "timestamp": current_time,
                "jsoned_results": serialized_results
            }

            if os.path.exists('instance/search_results.json'):
                with open('instance/search_results.json', 'r') as file:
                    data = json.load(file)
            else:
                data = []
            data.append(timed_results)

            with open('instance/search_results.json', 'w') as file:
                json.dump(data, file, indent=4)
            logger.info(f"Search performed by user_id: {current_user.id}")
        if not results:
            flash("No books met your search criteria.", "error")

    return render_template('search.html', form=form, results=results, count=len(results), saved_searches=saved_searches)


@bp.route("/saved_search/<search_id>", methods=["GET"])
@login_required
def load_saved_search(search_id: str) -> Response:
    """
    Load and display a saved search based on the provided search ID.

    This function retrieves a saved search from a JSON file based on the provided search ID. If the search ID
    matches one of the saved searches, it loads the search results and renders them on the search page. If the
    search ID is not found, the user is redirected back to the search page with an error message.

    Args:
        search_id (str): The unique identifier for the saved search.

    Returns:
        Response: An HTTP response object that renders the `search.html` template with the search results if the
                  search ID is found. If the search ID is not found, it redirects to the search page with an error
                  message.
    """
    if os.path.exists('instance/search_results.json'):
        with open('instance/search_results.json', 'r') as file:
            saved_searches = json.load(file)
        saved_search = next((item for item in saved_searches if item["search_id"] == search_id), None)
        if saved_search:
            results = saved_search['jsoned_results']
            logger.info(f"Saved search results accessed by user_id: {current_user.id}")
            return render_template('search.html', form=None, results=results, count=len(results),
                                   saved_searches=saved_searches)
    flash("Saved search results not found.", "error")
    return redirect(url_for('main.search'))


@bp.route("/all_ratings", methods=["GET"])
def all_ratings() -> Response:
    """
    Retrieve and display all books with their average ratings.

    This function queries all books from the database and calculates their average ratings. It filters out books
    that do not have an average rating, sorts the remaining books by their average rating in descending order,
    and then renders the `all_ratings.html` template with the sorted list of books.

    Returns:
        Response: An HTTP response object that renders the `all_ratings.html` template with a list of books sorted
                  by their average ratings.
    """
    books = Book.query.all()
    books_with_avg_rating = [(book, book.avg_rating) for book in books if book.avg_rating is not None]
    sorted_books_query = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total = len(sorted_books_query)
    start = (page - 1) * per_page
    end = start + per_page
    sorted_books = sorted_books_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("all_ratings.html", sorted_books=sorted_books, pagination=pagination, start_num=start_num)


@bp.route("/all_reviews", methods=["GET"])
def all_reviews() -> Response:
    """
    Retrieve and display all books with their review counts.

    This function queries all books from the database and counts the number of reviews associated with each book.
    It sorts the books by the number of reviews in descending order and renders the `all_reviews.html` template
    with the sorted list of books.

    Returns:
        Response: An HTTP response object that renders the `all_reviews.html` template with a list of books sorted
                  by their review counts.
    """
    books = Book.query.all()
    books_with_review_count = [(book, len(Review.query.filter_by(book_id=book.id).all())) for book in books]
    sorted_books_query = sorted(books_with_review_count, key=lambda x: x[1], reverse=True)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total = len(sorted_books_query)
    start = (page - 1) * per_page
    end = start + per_page
    sorted_books = sorted_books_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("all_reviews.html", sorted_books=sorted_books, pagination=pagination, start_num=start_num)


@bp.route("/all_read_listed", methods=["GET"])
def all_read_listed() -> Response:
    """
    Retrieve and display all books with their read list counts.

    This function queries all books from the database and counts the number of times each book has been added to users'
    read lists. It sorts the books by the count of read list entries in descending order and renders the
    `all_read_listed.html` template with the sorted list of books.

    Returns:
        Response: An HTTP response object that renders the `all_read_listed.html` template with a list of books sorted
                  by their read list counts.
    """
    books = Book.query.all()
    books_with_read_list_count = [(book, len(ToRead.query.filter_by(book_id=book.id).all())) for book in books]
    sorted_books_query = sorted(books_with_read_list_count, key=lambda x: x[1], reverse=True)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total = len(sorted_books_query)
    start = (page - 1) * per_page
    end = start + per_page
    sorted_books = sorted_books_query[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("all_read_listed.html", sorted_books=sorted_books, pagination=pagination, start_num=start_num)


def recommended_for_each_book(best_book: int) -> List[Tuple[Book, float]]:
    """
    Generate a list of recommended books based on user ratings.

    This function generates a list of books recommended for the current user based on their rating of a specific book.
    It performs the following steps:
    1. Finds all books rated 5 by the current user.
    2. Identifies users who have rated the same book with a rating of 5.
    3. Collects books rated 5 by these similar users that the current user hasn't rated.
    4. Returns a sorted list of these books based on their average rating in descending order.

    Args:
        best_book (int): The ID of the book that the current user has rated highly (rating of 5).

    Returns:
        List[Tuple[Book, float]]: A list of tuples where each tuple contains a `Book` object and its average rating,
                                  sorted by the average rating in descending order. Only books that are recommended
                                  based on the current user's ratings and those of similar users are included.
    """
    if best_book:
        your_rated5 = Rating.query.filter_by(user_id=current_user.id, rating=5).all()
        book_ids_all = [rating.book_id for rating in your_rated5]
        your_rated5 = Rating.query.filter_by(user_id=current_user.id, rating=5, book_id=best_book).all()
        book_ids = [rating.book_id for rating in your_rated5]
        users_alike = Rating.query.filter(Rating.book_id.in_(book_ids), Rating.rating == 5,
                                          Rating.user_id != current_user.id).all()
        users_alike_ids = [user.user_id for user in users_alike]
        books_alike = Rating.query.filter(Rating.user_id.in_(users_alike_ids),
                                          Rating.rating == 5, ~Rating.book_id.in_(book_ids_all)).all()
        recommended_books_ids = set([book.book_id for book in books_alike])
        books = Book.query.all()
        books_with_avg_rating = [(book, book.avg_rating) for book in books if book.id in recommended_books_ids
                                 and book.avg_rating is not None]
        sorted_books = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)
        return sorted_books


@bp.route("/recommended_for_you", methods=["GET"])
@login_required
def recommended_for_you() -> Response:
    """
    Generate book recommendations based on the current user's high-rated books.

    This view function performs the following steps:
    1. Checks if the current user has rated any books with a rating of 5.
    2. Retrieves books that the user has rated 5 and finds other users who rated those books 5.
    3. Identifies books rated 5 by similar users that the current user hasn't rated.
    4. Compiles recommendations based on the high-rated books and sorts them by average rating.
    5. For each book the user rated 5, additional recommendations are generated using `recommended_for_each_book`.

    If the user has not given any books a rating of 5, a flash message is shown and the user is redirected to the
    homepage.

    Returns:
        Flask Response: Renders the `recommended_for_you.html` template with the following context:
            - `sorted_books`: A list of recommended books sorted by average rating in descending order.
            - `separate_results`: A list of tuples where each tuple contains a book rated 5 by the user and
              a list of recommended books for that particular book.
    """
    your_rated5 = Rating.query.filter_by(user_id=current_user.id, rating=5).all()
    if not your_rated5:
        flash("You have not given any book rating 5 yet. No personal recommendations available", "info")
        return redirect('/')
    book_ids = [rating.book_id for rating in your_rated5]
    your_rated5_books = Book.query.filter(Book.id.in_(book_ids)).all()
    users_alike = Rating.query.filter(Rating.book_id.in_(book_ids), Rating.rating == 5,
                                      Rating.user_id != current_user.id).all()
    users_alike_ids = [user.user_id for user in users_alike]
    books_alike = Rating.query.filter(Rating.user_id.in_(users_alike_ids),
                                      Rating.rating == 5, ~Rating.book_id.in_(book_ids)).all()
    recommended_books_ids = set([book.book_id for book in books_alike])
    books = Book.query.all()
    books_with_avg_rating = [(book, book.avg_rating) for book in books if book.id in recommended_books_ids
                             and book.avg_rating is not None]
    sorted_books = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)
    separate_results_list = []
    for book in your_rated5_books:
        original_book = book
        recommended_books = recommended_for_each_book(book.id)
        separate_results_list.append((original_book, recommended_books))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    total = len(separate_results_list)
    start = (page - 1) * per_page
    end = start + per_page
    separate_results = separate_results_list[start:end]
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    start_num = start + 1

    return render_template("recommended_for_you.html", sorted_books=sorted_books, separate_results=separate_results, pagination=pagination, start_num=start_num)
