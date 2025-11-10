"""Quick forms for simplified data entry."""
from datetime import date
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
    DecimalField, StringField, SelectField, DateField,
    SelectField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class QuickExpenseForm(FlaskForm):
    """Simplified form for quick expense entry."""
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=Decimal('0.01'), message='Amount must be greater than 0')
    ])
    description = StringField('Description', validators=[
        DataRequired(), Length(1, 128)
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[Optional()], default=date.today)
    payment_method = SelectField('Payment Method', validators=[Optional()], choices=[
        ('', 'Payment Method'),
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('digital_wallet', 'Digital Wallet')
    ])
    is_recurring = BooleanField('Recurring')
    submit = SubmitField('Add Expense')