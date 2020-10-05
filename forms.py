from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, SelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email, ValidationError, DataRequired
from models import *
from werkzeug.security import check_password_hash
from wtforms.fields.html5 import DateField, TimeField


def invalidCredentials(form, field):

    email_e = form.email.data
    password_e = field.data

    userOb = User.query.filter_by(email=email_e).first()
    if userOb is None:
        raise ValidationError("Username or password is incorrect")
    elif not check_password_hash(userOb.password, password_e):
        raise ValidationError("Username or password is incorrect")


def checkwhitespaces(form, field):

    t = field.data
    field.data = t.strip()

    if field.data == '':
        raise ValidationError("Please enter a valid " + str(field.label))


class SignUp(FlaskForm):

    name = StringField('name',
                       validators=[InputRequired(), checkwhitespaces])

    email = StringField('email',
                        validators=[InputRequired(),
                                    Email("This field requires a valid email address")])

    password = PasswordField('password',
                             validators=[InputRequired(),
                                         Length(min=5, max=20)])

    confirmPassword = PasswordField('confirmPassword',
                                    validators=[InputRequired(), EqualTo('password', message="Passwords must match")])


class Login(FlaskForm):

    email = StringField('email',
                        validators=[InputRequired(), checkwhitespaces])

    password = PasswordField('password',
                             validators=[InputRequired(), invalidCredentials])


class CreateTeam(FlaskForm):

    team_name = StringField('team name',
                            validators=[InputRequired(), checkwhitespaces])

    team_description = StringField('team description',
                                   validators=[InputRequired(), checkwhitespaces])

    submit = SubmitField('Create')


class NewTask(FlaskForm):
    task_name = StringField('task name', validators=[
                            InputRequired(), checkwhitespaces])
    task_desc = StringField('team description', validators=[
                            InputRequired(), checkwhitespaces])
    user_team = SelectField(coerce=str, validate_choice=True)
    user_email = SelectField(coerce=str, validate_choice=True)
    deadline_date = DateField('deadline_date', validators=[DataRequired()])
