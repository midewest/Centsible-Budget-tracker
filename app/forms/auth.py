"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError
)
from ..models import User

class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Check username is not already taken."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already taken.')
    
    def validate_email(self, field):
        """Check email is not already registered."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered.')