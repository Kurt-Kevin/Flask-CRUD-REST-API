from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
import os
import traceback

######################### Setup #########################

# Initialize app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)


######################### Model & Schema #########################

# Movie Class/Model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(80), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(200), nullable=False)


######################### APIs #########################

# Create a movie
@app.route('/movie/create', methods=['POST'])
def create_movie():
    try:
        movie_dict = {
            'title': request.json['title'],
            'director': request.json['director'],
            'release_year': request.json['release_year'],
            'genre': request.json['genre']
        }
        new_movie = Movie(**movie_dict)
        db.session.add(new_movie)
        db.session.commit()
        movie_dict['id'] = new_movie.id
        return jsonify(movie_dict), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# Get all movies
@app.route('/movie/all', methods=['GET'])
def get_all_movies():
    all_movies = Movie.query.all()
    movie_list = []
    for movie in all_movies:
        movie_list.append({
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'genre': movie.genre,
            'id': movie.id
        })
    return jsonify(movie_list)


# Get a single movie
@app.route('/movie/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    if movie is None:
        return jsonify({'error': f'No movie found with the id {id}'}), 404
    movie_dict = {
        'title': movie.title,
        'director': movie.director,
        'release_year': movie.release_year,
        'genre': movie.genre,
        'id': movie.id
    }
    return jsonify(movie_dict)


# Search movie by title
@app.route('/movie/search/title/<title>', methods=['GET'])
def search_movie_title(title):
    all_movies = Movie.query.filter(Movie.title.contains(title))
    if not all_movies:
        return jsonify({'error': f'No movie found with the title {title}'}), 404
    movie_list = []
    for movie in all_movies:
        movie_list.append({
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'genre': movie.genre,
            'id': movie.id
        })
    return jsonify(movie_list)


# Update a movie
@app.route('/movie/update/<id>', methods=['PUT'])
def update_movie(id):
    try:
        movie = Movie.query.get(id)
        if movie is None:
            return jsonify({'error': f'No movie found with the id {id}'}), 404
        movie.title = request.json.get('title', movie.title)
        movie.director = request.json.get('director', movie.director)
        movie.release_year = request.json.get('release_year', movie.release_year)
        movie.genre = request.json.get('genre', movie.genre)
        db.session.commit()
        movie_dict = {
            'title': movie.title,
            'director': movie.director,
            'release_year': movie.release_year,
            'genre': movie.genre,
            'id': movie.id
        }
        return jsonify(movie_dict)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# Delete a movie
@app.route('/movie/delete/<id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.query.get(id)
    if movie is None:
        return jsonify({'error': f'No movie found with the id {id}'}), 404
    db.session.delete(movie)
    db.session.commit()
    movie_dict = {
        'title': movie.title,
        'director': movie.director,
        'release_year': movie.release_year,
        'genre': movie.genre,
        'id': movie.id
    }
    return jsonify(movie_dict)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
