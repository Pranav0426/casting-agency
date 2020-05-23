import os
from flask import Flask, request, abort, jsonify
from flask import render_template, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor, db
from auth import AuthError, requires_auth, requires_signed_in
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
import constants

AUTH0_CALLBACK_URL = constants.AUTH0_CALLBACK_URL
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_BASE_URL = 'https://' + os.environ['AUTH0_DOMAIN']
AUTH0_AUDIENCE = constants.AUTH0_AUDIENCE


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = "super secret key"
    setup_db(app)

    # setup cross origin
    CORS(app)

    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')

        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    # Setup home route

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL,
                                        audience=AUTH0_AUDIENCE)

    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint

        res = auth0.authorize_access_token()
        token = res.get('access_token')

        # Store the user information in flask session.
        session['jwt_token'] = token

        return redirect('/dashboard')

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for(
            'index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/dashboard')
    @requires_signed_in
    def dashboard():
        return render_template('dashboard.html',
                               token=session['jwt_token'],
                               )

    """Movies Routes"""

    # Route for getting all movies
    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies(jwt):
        """Get all movies route"""

        movies = Movie.query.all()

        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in movies],
        }), 200

    # Route for getting a specific movie
    @app.route('/movies/<int:id>')
    @requires_auth('get:movies')
    def get_movie_by_id(jwt, id):
        """Get a specific movie route"""
        movie = Movie.query.get(id)

        # return 404 if there is no movie with id
        if movie is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'movie': movie.format(),
            }), 200

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_movie(jwt):
        """Create a movie route"""
        # Process request data
        data = request.get_json()
        title = data.get('title', None)
        release_date = data.get('release_date', None)

        # return 400 for empty title or release date
        if title is None or release_date is None:
            abort(400)

        movie = Movie(title=title, release_date=release_date)

        try:
            movie.insert()
            return jsonify({
                'success': True,
                'movie': movie.format()
            }), 201
        except Exception:
            abort(500)

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def patch_movie(jwt, id):
        """Update a movie route"""

        data = request.get_json()
        title = data.get('title', None)
        release_date = data.get('release_date', None)

        movie = Movie.query.get(id)

        if movie is None:
            abort(404)

        if title is None or release_date is None:
            abort(400)

        movie.title = title
        movie.release_date = release_date

        try:
            movie.update()
            return jsonify({
                'success': True,
                'movie': movie.format()
            }), 200
        except Exception:
            abort(500)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(jwt, id):
        """Delete a movie route"""
        movie = Movie.query.get(id)

        if movie is None:
            abort(404)
        try:
            movie.delete()
            return jsonify({
                'success': True,
                'message':
                f'movie id {movie.id}, titled {movie.title} was deleted',
            })
        except Exception:
            db.session.rollback()
            abort(500)

    """Actors Routes"""

    @app.route('/actors')
    @requires_auth('get:actors')
    def get_actors(jwt):
        """Get all actors route"""

        actors = Actor.query.all()

        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors],
        }), 200

    @app.route('/actors/<int:id>')
    @requires_auth('get:actors')
    def get_actor_by_id(jwt, id):
        """Get all actors route"""
        actor = Actor.query.get(id)

        if actor is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'actor': actor.format(),
            }), 200

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_actor(jwt):
        """Get all movies route"""
        data = request.get_json()
        name = data.get('name', None)
        age = data.get('age', None)
        gender = data.get('gender', None)

        actor = Actor(name=name, age=age, gender=gender)

        if name is None or age is None or gender is None:
            abort(400)

        try:
            actor.insert()
            return jsonify({
                'success': True,
                'actor': actor.format()
            }), 201
        except Exception:
            abort(500)

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def patch_actor(jwt, id):
        """Update an actor Route"""

        data = request.get_json()
        name = data.get('name', None)
        age = data.get('age', None)
        gender = data.get('gender', None)

        actor = Actor.query.get(id)

        if actor is None:
            abort(404)

        if name is None or age is None or gender is None:
            abort(400)

        actor.name = name
        actor.age = age
        actor.gender = gender

        try:
            actor.update()
            return jsonify({
                'success': True,
                'actor': actor.format()
            }), 200
        except Exception:
            abort(500)

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(jwt, id):
        """Delete an actor Route"""
        actor = Actor.query.get(id)

        if actor is None:
            abort(404)
        try:
            actor.delete()
            return jsonify({
                'success': True,
                'message':
                f'actor id {actor.id}, named {actor.name} was deleted',
            })
        except Exception:
            db.session.rollback()
            abort(500)

    # Error Handling
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def handle_auth_error(exception):
        response = jsonify(exception.error)
        response.status_code = exception.status_code
        return response

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
