"""Budget management forms."""
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
    DecimalField, IntegerField, TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Optional, NumberRange
)

class CategoryBudgetForm(FlaskForm):
    """Form for setting category budgets."""
    budget_amount = DecimalField('Monthly Budget Amount', validators=[
        DataRequired(),
        NumberRange(min=Decimal('0.01'), message='Budget must be greater than 0')
    ])
    alert_threshold = IntegerField('Alert Threshold (%)', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='Must be between 1 and 100')
    ], default=80)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Budget')

class UserBudgetForm(FlaskForm):
    """Form for setting user's overall budget and income."""
    monthly_income = DecimalField('Monthly Income', validators=[
        Optional(),
        NumberRange(min=Decimal('0'), message='Income cannot be negative')
    ])
    total_budget = DecimalField('Total Monthly Budget', validators=[
        Optional(),
        NumberRange(min=Decimal('0'), message='Budget cannot be negative')
    ])
    submit = SubmitField('Save Settings')