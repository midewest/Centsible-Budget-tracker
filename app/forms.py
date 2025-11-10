"""Forms for Centsible Budget Tracker."""
from datetime import date
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, DecimalField, DateField, SelectField,
    TextAreaField, BooleanField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
)
from .models import User

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

class ExpenseForm(FlaskForm):
    """Form for adding/editing expenses."""
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=Decimal('0.01'), message='Amount must be greater than 0')
    ])
    description = StringField('Description', validators=[
        DataRequired(), Length(1, 128)
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    payment_method = SelectField('Payment Method', validators=[Optional()], choices=[
        ('', 'Select Method'),
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('digital_wallet', 'Digital Wallet'),
        ('other', 'Other')
    ])
    is_recurring = BooleanField('Recurring Expense')
    recurrence_frequency = SelectField('Recurrence', choices=[
        ('', 'Not Recurring'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ])
    receipt_note = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Save Expense')

class CategoryForm(FlaskForm):
    """Form for adding/editing expense categories."""
    name = StringField('Category Name', validators=[
        DataRequired(), Length(1, 64)
    ])
    icon = StringField('Icon (Font Awesome class)', validators=[Optional()])
    color = StringField('Color (Hex code)', validators=[Optional()])
    budget_amount = DecimalField('Monthly Budget', validators=[Optional()])
    submit = SubmitField('Save Category')

    def validate_color(self, field):
        """Validate hex color code format."""
        if field.data and not field.data.startswith('#'):
            field.data = f'#{field.data}'
        if field.data and not len(field.data) in [4, 7]:  # #RGB or #RRGGBB
            raise ValidationError('Invalid hex color code')