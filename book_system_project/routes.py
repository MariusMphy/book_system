from flask import Flask, render_template, redirect, request, url_for, flash, session
from book_system_project import db, app, login_manager, bcrypt
from book_system_project.models import Book, User, Rating, Author, Genre, ToRead, Review
from book_system_project.forms import (RegisterForm, LoginForm, BookForm, AuthorForm, RateBook, EditUserForm,
                                       ChangePasswordForm, SortRating, ToReadForm, WriteReviewForm, SearchForm)
from flask_login import login_user, login_required, logout_user, current_user
import csv
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


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


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book_details(book_id):
    form = ToReadForm()
    book = Book.query.get_or_404(book_id)
    author = book.author
    genres = book.genres
    review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else "Not rated"
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
    toread = ToRead.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    return render_template('book.html', form=form, book=book, author=author, genres=genres, avg_rating=avg_rating,
                           rating=rating, toread=toread, review=review)


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
            flash("Profile updated successfully", "success")
        else:
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
            flash("Old password is incorrect", "error")
            return render_template('change_password.html', form=form)
        if new_password != confirm_password:
            flash('Passwords, do not match!', 'error')
            return render_template('change_password.html', form=form)
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
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

    return render_template("your_ratings.html", form=form, sorted_books=sorted_books)


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


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    title = form.title.data
    author = form.author.data
    genre = form.genre.data
    rating_min = form.rating_min.data
    rating_max = form.rating_max.data
    review = form.review.data

    return render_template('search.html', form=form, title=title, author=author, genre=genre,
                           rating_min=rating_min, rating_max=rating_max, review=review)