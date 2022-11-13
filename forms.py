from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RateMovieForm(FlaskForm):
    new_rating = StringField('Your Rating', validators=[DataRequired()])
    new_review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddMovieForm(FlaskForm):
    new_movie = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField('Add')
