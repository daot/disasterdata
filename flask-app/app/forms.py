from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    keyword = StringField('Enter a keyword to search', validators = [DataRequired()])
    submit = SubmitField('Submit')