from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new_collection.db"

db = SQLAlchemy()
db.init_app(app)

API_KEY = "b0f3d283345e896bfb540a04ad30a453"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

class ReviewForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g 7.2', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# with app.app_context():
#     db.create_all()
#
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()
#
#     second_movie = Movie(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()

Bootstrap5(app)


@app.route("/", methods=["GET"])
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    rank = len(all_movies)
    for each in all_movies:
        each.ranking = rank
        rank -= 1
    db.session.commit()


    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = ReviewForm()
    if form.validate_on_submit():
        id = request.args.get('id')
        print(id)
        movie_to_update = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form)

@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["POST", "GET"])
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        print("form validated")

        url = "https://api.themoviedb.org/3/search/movie"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMGYzZDI4MzM0NWU4OTZiZmI1NDBhMDRhZDMwYTQ1MyIsInN1YiI6IjY1OTQ3OThjOTQ0YTU3MGFhZjFmMzlhNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LlL5WbEdcJZgbcUrCEh92aRV1__tA1iKZl0cdiEauPY"
        }

        params = {
            "query": add_form.title.data,
            "include_adult": False,
            "language": "en - US",
            "page": 1
        }

        # movies = []
        response = requests.get(url=url, headers=headers, params=params)
        response_results = response.json()['results']
        # if response_results:
        #     for result in response_results:
        #         movie = (result["title"], result["release_date"])
        #         movies.append(movie)
        # print(movies)
        return render_template('select.html', movies=response_results)

    return render_template('add.html', form=add_form)

@app.route('/select')
def select():
    id = request.args.get('id')
    print(id)
    if id:
        url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMGYzZDI4MzM0NWU4OTZiZmI1NDBhMDRhZDMwYTQ1MyIsInN1YiI6IjY1OTQ3OThjOTQ0YTU3MGFhZjFmMzlhNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LlL5WbEdcJZgbcUrCEh92aRV1__tA1iKZl0cdiEauPY"
        }

        response = requests.get(url, headers=headers)
        response.encoding = 'UTF-8'
        response_results = response.json()
        print(response_results)

        new_movie = Movie(
                title=response_results['title'],
                year=response_results['release_date'].split('-')[0],
                description=response_results['overview'],
                img_url="https://image.tmdb.org/t/p/original/"+response_results['poster_path']
            )
        db.session.add(new_movie)
        db.session.commit()


    return redirect(url_for('edit', id=new_movie.id))

@app.route("/try")
def trial():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
