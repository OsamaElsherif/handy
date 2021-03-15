from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from handy.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone Numper', 
                        validators=[DataRequired()])
    city = StringField('City', 
                        validators=[DataRequired()])
    state = StringField('State', 
                        validators=[DataRequired()])
    password = PasswordField('Password',
                            validators=[DataRequired(), Length(min=2, max=20)])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    usertype = RadioField('User Type', choices=[('Client'),('Handicraft')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This account is already exist!!')


class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired(), Length(min=2, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccount(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    description = TextAreaField('Description')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    major = RadioField('User Type', choices=[('Carpenter'),('Electration'),('Painter'),('Plumber'),('Client')])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This account is already exist!!')


class CreateRequestForm(FlaskForm):
    jop_title = StringField('Jop Title', validators=[DataRequired()])
    jop_major = StringField('Jop Major', validators=[DataRequired()])
    jop_description = TextAreaField('Jop Description', validators=[DataRequired()])
    submit = SubmitField('Make Request')


class ApplyForJopForm(FlaskForm):
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Apply')


class HireForm(FlaskForm):
    submit = SubmitField('Hire')

class AcceptanceRejection(FlaskForm):
    id = StringField('ID',
                            validators=[DataRequired()])
    Acceptance = SubmitField('Accept')
    Rejection = SubmitField('Reject')

class RequestResetForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Send Email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account for this email, you must register firsted!!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired(), Length(min=2, max=20)])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
