from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField


class EditInfoForm(FlaskForm):
    courier_type = TextAreaField("My Type")
    regions = TextAreaField("My Regions")
    working_hours = TextAreaField("My Working Hours")
    submit = SubmitField('Update')
