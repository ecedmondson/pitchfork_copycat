from flask_wtf import FlaskForm
from wtforms import Form, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    choices = [('Artist', 'Artist'),
               ('Album', 'Album'),
               ('User', 'User'),
               ('Genre', 'Genre')]
    select_search = SelectField('Search:', [DataRequired()], choices=choices)
    search_keyword = StringField("Insert search:", [DataRequired()])
    submit = SubmitField("Submit")
