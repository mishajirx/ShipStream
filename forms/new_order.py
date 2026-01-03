from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, FloatField, TimeField
from wtforms.validators import DataRequired, ValidationError

from data.help_functions import check_address
from data.variables import regions_table


def validate_region(form, field):
    if field.data not in regions_table.keys():
        raise ValidationError("Region must exist in RF")


def validate_weight(form, field):
    if not (0.1 <= field.data <= 50):
        raise ValidationError("Weight must be between 0.1 and 50")


def validate_address(form, field):
    if not check_address(field.data):
        raise ValidationError("Address is invalid")


class MakeOrderForm(FlaskForm):
    weight = FloatField('Order Weight (kg)', validators=[DataRequired("Invalid weight format"), validate_weight])
    region = IntegerField('Order Region',
                          validators=[DataRequired(message="Invalid region format"), validate_region])
    address = StringField('Address (Street sufficient)',
                          validators=[DataRequired(message="Enter address"), validate_address])
    workhours_start = TimeField("Delivery time from",
                                validators=[DataRequired(message="Invalid start time format")])
    workhours_end = TimeField("Delivery time to",
                              validators=[DataRequired(message="Invalid end time format")])
    submit = SubmitField('Place Order')
