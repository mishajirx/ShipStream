from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, RadioField, BooleanField, SelectField, \
    validators
from wtforms.fields import EmailField, IntegerField, TimeField
from wtforms.validators import DataRequired


class EditAboutForm(FlaskForm):
    is_courier = BooleanField("I agree to the terms of work")

    type_of_courier = SelectField("Courier Type",
                                  choices=[('foot', "Foot"), ('bike', "Bike"), ('car', "Car")])
    region = IntegerField("Your region (number)", validators=[validators.DataRequired(message="Invalid region format")])
    workhours_start = TimeField("Work start time",
                                validators=[validators.DataRequired(message="Invalid start time format")])
    workhours_end = TimeField("Work end time",
                              validators=[validators.DataRequired(message="Invalid end time format")])

    submit = SubmitField('Submit Application')
