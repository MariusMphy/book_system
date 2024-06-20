from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import IntegerField, StringField, EmailField, PasswordField, SelectField, FloatField, TextAreaField, SubmitField


class RegisterForm(FlaskForm):
    # email = EmailField("Email: ", validators=[DataRequired(), Email()])
    name = StringField("Name: ")
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    name = StringField("Name: ")
    submit = SubmitField("Login")


class BookForm(FlaskForm):
    title = StringField("Name: ", validators=[DataRequired(), Length(min=1, max=256)])
    author = SelectField("Author: ")
    genre = SelectField("Genre: ")
    submit = SubmitField("Add book")
