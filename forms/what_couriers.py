from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class NewCourierForm(FlaskForm):
    couriers = SelectMultipleField(label='Want to be couriers', coerce=int)
    submit = SubmitField('Hire')
