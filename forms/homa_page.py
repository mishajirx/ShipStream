from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class HomeForm(FlaskForm):
    # email = EmailField('Email', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember me')
    # submit = SubmitField('Log in')
    status = SubmitField("Order", validators=[DataRequired()])
    pass
