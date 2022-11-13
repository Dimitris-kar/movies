from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from forms import RateMovieForm, AddMovieForm
from sqlalchemy import exc
import requests

app = Flask(__name__)

# creating the database
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
# Optional: But it will silence the deprecation warning in the console.(if needed)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# adding Bootstrap5
bootstrap = Bootstrap5(app)

# API components for TMDA(The Movie Database API)
TMDB_API_KEY = "b4947a55aee7b84027a755b5622b1ca8"

# example API_request
api_request = 'https://api.themoviedb.org/3/movie/550?api_key=b4947a55aee7b84027a755b5622b1ca8'


# create a table in the database
class Movies(db.Model):
    id = db.Column('movie_id', db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=False)


# create finally the database and the table(s)
with app.app_context():
    db.create_all()


# all routes
@app.route("/")
def home():
    # create a query of all movies in rating order
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit/<movie_id>", methods=['GET', 'POST'])
def edit(movie_id):
    edit_form = RateMovieForm()
    movie = db.get_or_404(Movies, movie_id)
    if edit_form.validate_on_submit():
        # declare new values for rating and review retrieved from form
        new_rating = request.form.get('new_rating')
        new_review = request.form.get('new_review')
        movie.rating = new_rating
        movie.review = new_review
        # commit the changes to database
        movie.verified = True
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', edit_form=edit_form, movie=movie)


@app.route("/delete/<movie_id>")
def delete(movie_id):
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    db.session.commit()
    # TODO: Appears a message on the screen that you have succesfully delete the movie for some seconds
    flash('You were successfully delete the movie')
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    # create the form
    add_form = AddMovieForm()
    if add_form.validate_on_submit():
        movie_title = request.form.get('new_movie')
        # work with the movie database API and send a request for the mathing titles and dates of release
        response = requests.get("https://api.themoviedb.org/3/search/movie", params={'api_key': TMDB_API_KEY,
                                                                                     'query': movie_title})
        response.raise_for_status()
        all_movies = response.json()['results']
        return render_template('select.html', all_movies=all_movies, message="")

    return render_template('add.html', add_form=add_form)


@app.route("/find/<movie_id>")
def find_movie(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=b4947a55aee7b84027a755b5622b1ca8")
    response.raise_for_status()
    new_movie = response.json()

    # add the new movie to the database
    new_movie = Movies(
        title=new_movie['original_title'],
        year=new_movie['release_date'].split("-")[0],
        description=new_movie['overview'],
        img_url=f"https://image.tmdb.org/t/p/w500{new_movie['poster_path']}"
    )
    try:
        db.session.add(new_movie)
        db.session.commit()
    except exc.IntegrityError:
        print("You have already add this movie into your list.")
        return render_template('select.html', message="This movie is already in your list. Can't have it twice.")
    else:
        return redirect(url_for('edit', movie_id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)

# TODO: raise ecxeption if the title you want to add is the same as one you already have
