from flask import render_template, redirect, request, url_for, flash, session
from book_system_project import db, app
from book_system_project.models import Book, User, Rating, Author, Genre


@app.route("/")
def home():
    return render_template("base.html")

