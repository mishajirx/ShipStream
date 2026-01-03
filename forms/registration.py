import phonenumbers
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError
from wtforms_alchemy import PhoneNumberField


class RegisterForm(FlaskForm):
    phone_number = PhoneNumberField("Phone number (format: +7 XXX XXX XX XX)", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    is_courier = BooleanField("I want to be a courier")
    s = "(For couriers: <type>;<region1>,<region2>,...;<WorkHours1(HH:MM-HH:MM)>,<WorkHours2>,..."
    about = TextAreaField("A bit about yourself " + s)
    submit = SubmitField('Register')
