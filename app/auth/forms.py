"""
Flask-WTF Forms for Authentication and User Profile Management.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User


class RegistrationForm(FlaskForm):
    """User account registration form with real-time uniqueness validation."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=30)]
    )
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters.')]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        """Ensure username is unique."""
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another.')

    def validate_email(self, email):
        """Ensure email is unique."""
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email already exists. Please log in.')


class LoginForm(FlaskForm):
    """User login form with remember-me capability."""
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Keep me signed in')
    submit = SubmitField('Log In')


class UpdateProfileForm(FlaskForm):
    """User profile update form for editing bio, username, and avatar."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=30)]
    )
    bio = TextAreaField(
        'Bio',
        validators=[Length(max=300, message='Bio cannot exceed 300 characters.')]
    )
    profile_image = FileField(
        'Profile Picture',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, png, webp)!')]
    )
    submit = SubmitField('Save Profile')

    def validate_username(self, username):
        """Ensure updated username is unique unless it is current user's."""
        if current_user.is_authenticated and username.data.strip() != current_user.username:
            user = User.query.filter_by(username=username.data.strip()).first()
            if user:
                raise ValidationError('That username is already taken. Please choose another.')
