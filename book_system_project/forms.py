from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, Optional
from wtforms import IntegerField, StringField, EmailField, PasswordField, SelectField, SelectMultipleField, FloatField, TextAreaField, SubmitField, DateField


class RegisterForm(FlaskForm):
    email = EmailField("Email: ", validators=[DataRequired(), Email(), Length(min=3, max=128)])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=3, max=128)])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(), Length(min=3, max=128)])
    name = StringField("Name: ", validators=[DataRequired(), Length(min=1, max=36)])
    phone = StringField("Phone: ", validators=[Optional(), Length(max=20)])
    date_of_birth = DateField("Date of birth: ", format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField("Gender: ", choices=[('', 'Chose gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    submit = SubmitField("Register")


class EditUserForm(FlaskForm):
    name = StringField("Name: ", validators=[Optional(), Length(min=1, max=36)])
    phone = StringField("Phone: ", validators=[Optional(), Length(max=20)])
    date_of_birth = DateField("Date of birth: ", format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField("Gender: ",
                         choices=[('', 'Chose gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField("Save")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password: ", validators=[DataRequired(), Length(min=3, max=128)])
    new_password = PasswordField("New password: ", validators=[DataRequired(), Length(min=3, max=128)])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = EmailField("Email: ", validators=[DataRequired(), Email()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Login')


class BookForm(FlaskForm):
    title = StringField("Title: ", validators=[DataRequired(), Length(min=1, max=256)])
    author = SelectField("Author: ")
    genre = SelectMultipleField("Genre: ")
    submit = SubmitField("Add book: ")


class AuthorForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired(), Length(min=1, max=256)])
    submit = SubmitField("Add author: ")


class RateBook(FlaskForm):
    rating = SelectField("Your rating: ", choices=[("", 'None'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[DataRequired()])
    submit = SubmitField("Rate book")

