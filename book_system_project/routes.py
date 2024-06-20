from flask import Flask, render_template, redirect, request, url_for, flash, session
from book_system_project import db, app, login_manager
from book_system_project.models import Book, User, Rating, Author, Genre, RegisterForm, LoginForm
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