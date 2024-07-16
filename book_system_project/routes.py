from flask import render_template, redirect, request, url_for, flash

from book_system_project import db, app, login_manager, bcrypt, logger
from book_system_project.models import Book, User, Rating, Author, Genre, ToRead, Review, book_genres
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


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route("/")
def home():
    books = Book.query.all()
    books_with_avg_rating = [(book, book.avg_rating) for book in books if book.avg_rating is not None]
    top5_books = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)[:5]

    books_with_review_count = [(book, len(Review.query.filter_by(book_id=book.id).all())) for book in books]
    top_reviewed_books = sorted(books_with_review_count, key=lambda x: x[1], reverse=True)[:5]

    books_with_read_list_count = [(book, len(ToRead.query.filter_by(book_id=book.id).all())) for book in books]
    top_read_listed_books = sorted(books_with_read_list_count, key=lambda x: x[1], reverse=True)[:5]

    return render_template("base.html", top5_books=top5_books, top_reviewed_books=top_reviewed_books,
                           top_read_listed_books=top_read_listed_books)


@app.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template("profile.html", user=user)


@app.route("/fill_db", methods=["GET", "POST"])
@login_required
def fill_db():
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /fill_db by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    return render_template('fill_db.html')


@app.route("/fill_book_db", methods=["GET", "POST"])
@login_required
def fill_book_db():
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


@app.route("/fill_user_db", methods=["GET", "POST"])
@login_required
def fill_user_db():
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


def randomize_review():
    with open('book_system_project/media/words3000.txt', 'r') as file:
        words = file.read()
    words = words.split()

    def get_result(word_list, sentence_length):
        sentence = ' '.join(choice(word_list) for _ in range(sentence_length))
        return sentence[0].upper() + sentence[1:]

    number_of_sentences = randint(5, 12)
    sentences = [get_result(words, randint(5, 15)) for _ in range(number_of_sentences)]
    return '. '.join(sentences) + '.'


@app.route("/fill_ratings", methods=["GET", "POST"])
@login_required
def fill_ratings():
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
            logger.info(f"Logged in user_id: {user.id}, email: {user.email}")
            flash(' You have logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            logger.warning(f"Failed to login in user_id: {user.id}, email: {user.email}")
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logger.info(f"Logged out user_id: {current_user.id}, email: {current_user.email}")
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('home'))


@app.route("/add_author", methods=["GET", "POST"])
@login_required
def add_author():
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


@app.route("/view_users", methods=["GET", "POST"])
@login_required
def view_users():
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
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')
    start_num = (page - 1) * per_page + 1
    if users:
        return render_template('view_users.html', users=users, pagination=pagination, start_num=start_num)
    return render_template('admin_page.html')


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
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
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)


@app.route("/view_books", methods=["GET", "POST"])
def view_books():
    books = Book.query.all()
    return render_template("view_books.html", books=books)


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book_details(book_id):
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
            return redirect(url_for('to_read'))
        flash('This book is already in your read list', 'error')
        return redirect(url_for('to_read'))

    toread = ToRead.query.filter_by(user_id=current_user.id, book_id=book_id).first() \
        if current_user.is_authenticated else None
    read_listed = len(ToRead.query.filter_by(book_id=book_id).all())
    return render_template('book.html', form=form, book=book, author=author, genres=genres, avg_rating=avg_rating,
                           rating=rating, toread=toread, review=review, review_count=review_count,
                           read_listed=read_listed)


@app.route("/rate_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def rate_book(book_id):
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
        return redirect(url_for('book_details', book_id=book_id))
    return render_template('rate_book.html', book=book, author=author, genres=genres, avg_rating=avg_rating,
                           current_rating=current_rating, form=form)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
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
            return redirect(url_for('edit_profile'))
    return render_template("edit_profile.html", form=form, current_email=current_email, current_name=current_name,
                           current_phone=current_phone, current_date_of_birth=current_date_of_birth,
                           current_gender=current_gender)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
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
        return redirect(url_for('home'))
    return render_template('change_password.html', form=form)


@app.route("/your_ratings", methods=["GET", "POST"])
@login_required
def your_ratings():
    form = SortRating()
    ratings_with_books = db.session.query(Rating, Book).join(Book).filter(Rating.user_id == current_user.id).all()
    rated_books = [{'book': book, 'rating': rating.rating, 'rating_id': rating.id} for rating, book in
                   ratings_with_books]

    sorted_books = sorted(rated_books, key=lambda x: x['rating_id'], reverse=True)
    if request.method == 'POST' and form.validate_on_submit():
        sorting = form.sorted.data
        if sorting == "best":
            sorted_books = sorted(rated_books, key=lambda x: x['rating'], reverse=True)
        elif sorting == "worst":
            sorted_books = sorted(rated_books, key=lambda x: x['rating'], reverse=False)
        elif sorting == "newest":
            sorted_books = sorted(rated_books, key=lambda x: x['rating_id'], reverse=True)
        elif sorting == "oldest":
            sorted_books = sorted(rated_books, key=lambda x: x['rating_id'], reverse=False)

    return render_template("your_ratings.html", form=form, sorted_books=sorted_books,
                           ratings_with_books=ratings_with_books)


@app.route("/to_read", methods=["GET", "POST"])
@login_required
def to_read():
    toread_list = db.session.query(ToRead, Book).join(Book).filter(ToRead.user_id == current_user.id).all()
    books = [{'book': book, 'toread': toread} for toread, book in toread_list]
    return render_template("to_read.html", books=books)


@app.route("/remove_to_read/<int:book_id>", methods=["GET", "POST"])
@login_required
def remove_to_read(book_id):
    toread_to_remove = ToRead.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if toread_to_remove:
        db.session.delete(toread_to_remove)
        db.session.commit()
        logger.info(f"User_id: {current_user.id}, removed book_id {book_id} from read list")
        flash('Book has been removed from your read list', 'success')
    else:
        flash('Book not found in your read list', 'error')
    return redirect(url_for('to_read'))


@app.route("/write_review/<int:book_id>", methods=["GET", "POST"])
@login_required
def write_review(book_id):
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
        return redirect(url_for('book_details', book_id=book_id))
    return render_template('write_review.html', form=form, review=old_review, book=book, author=author)


@app.route("/your_reviews", methods=["GET", "POST"])
@login_required
def your_reviews():
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

    rev_info = [
        {
            "review": review.review,
            "book_title": review.title,
            "book_id": review.book_id,
            "author_name": review.author_name,
            "user_name": review.user_name,

        }
        for review in reviews
    ]
    return render_template('your_reviews.html', rev_info=rev_info)


@app.route("/book_reviews/<int:book_id>", methods=["GET", "POST"])
def book_reviews(book_id):
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

    sorted_rev_info = sorted(rev_info, key=lambda x: x['rating_id'], reverse=True)
    if request.method == 'POST' and form.validate_on_submit():
        sorting = form.sorted.data
        if sorting == "best":
            sorted_rev_info = sorted(rev_info, key=lambda x: x['rating'], reverse=True)
        elif sorting == "worst":
            sorted_rev_info = sorted(rev_info, key=lambda x: x['rating'], reverse=False)
        elif sorting == "newest":
            sorted_rev_info = sorted(rev_info, key=lambda x: x['rating_id'], reverse=True)
        elif sorting == "oldest":
            sorted_rev_info = sorted(rev_info, key=lambda x: x['rating_id'], reverse=False)

    return render_template('book_reviews.html', form=form, rev_info=sorted_rev_info, book=book, author=author)


@app.route("/admin_page", methods=["GET", "POST"])
@login_required
def admin_page():
    if current_user.name != "Admin":
        logger.warning(f"Unauthorized access attempt to /admin_page by user: {current_user.id}")
        flash("You dont have permits to access this page!", "error")
        return redirect('/')
    logger.info(f"Admin_page accessed by admin: {current_user.id}")
    return render_template('admin_page.html')


@app.route("/search", methods=["GET", "POST"])
def search():
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


@app.route("/saved_search/<search_id>", methods=["GET"])
@login_required
def load_saved_search(search_id):
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
    return redirect(url_for('search'))


@app.route("/all_ratings", methods=["GET", "POST"])
def all_ratings():
    books = Book.query.all()
    books_with_avg_rating = [(book, book.avg_rating) for book in books if book.avg_rating is not None]
    sorted_books = sorted(books_with_avg_rating, key=lambda x: x[1], reverse=True)
    return render_template("all_ratings.html", sorted_books=sorted_books)


@app.route("/all_reviews", methods=["GET", "POST"])
def all_reviews():
    books = Book.query.all()
    books_with_review_count = [(book, len(Review.query.filter_by(book_id=book.id).all())) for book in books]
    sorted_books = sorted(books_with_review_count, key=lambda x: x[1], reverse=True)
    return render_template("all_reviews.html", sorted_books=sorted_books)


@app.route("/all_read_listed", methods=["GET", "POST"])
def all_read_listed():
    books = Book.query.all()
    books_with_read_list_count = [(book, len(ToRead.query.filter_by(book_id=book.id).all())) for book in books]
    sorted_books = sorted(books_with_read_list_count, key=lambda x: x[1], reverse=True)
    return render_template("all_read_listed.html", sorted_books=sorted_books)


def recommended_for_each_book(best_book):
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


@app.route("/recommended_for_you", methods=["GET", "POST"])
@login_required
def recommended_for_you():
    your_rated5 = Rating.query.filter_by(user_id=current_user.id, rating=5).all()
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
    separate_results = []
    for book in your_rated5_books:
        original_book = book
        recommended_books = recommended_for_each_book(book.id)
        separate_results.append((original_book, recommended_books))
    return render_template("recommended_for_you.html", sorted_books=sorted_books, separate_results=separate_results)
