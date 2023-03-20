from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class CreateNewListForm(FlaskForm):
    name = StringField("List Name", validators=[DataRequired()])
    submit = SubmitField("Create New List")

class CreateNewListItemForm(FlaskForm):
    body = StringField("Thing to Do", validators=[DataRequired()])
    submit = SubmitField("Submit")

class EditListItemForm(FlaskForm):
    body = StringField("Thing to Do", validators=[DataRequired()])
    submit = SubmitField("Edit")

class EditListForm(FlaskForm):
    name = StringField("List Name", validators=[DataRequired()])
    submit = SubmitField("Edit")