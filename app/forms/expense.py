"""Expense management forms."""
from datetime import date
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
    StringField, DecimalField, DateField, SelectField,
    TextAreaField, BooleanField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)

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