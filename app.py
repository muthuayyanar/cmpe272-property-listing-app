from pymongo import MongoClient
from flask import Flask, render_template

############

from os import environ as env
from os import path as path
from flask import Flask, jsonify, request, session, redirect, render_template, url_for, send_from_directory
from werkzeug.exceptions import HTTPException
from functools import wraps
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from dotenv import load_dotenv

#from bookstore.version import API_VERSION
import constants

import json
import jwt
import datetime

app = Flask(__name__)
dotenv_path = path.join(path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

JWT_SECRET_KEY = env.get('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = "aquickfoxjumpedovertheriver"

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def fulfillment_token(auth):
    if auth and auth.password == 'secret':
        user_name = auth.username
    else:
        return jsonify_error("Unauthorized", 401)
        
    try:
        token = jwt.encode({'user': user_name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)}, JWT_SECRET_KEY)
        return jsonify({'token': token.decode()})
    except Exception as ex:
        print(ex)
        return jsonify_error("Unexpected error while creating the auth token.", 500)

def jsonify_error(message, staus_code):
    error = {
        'status_code': staus_code,
        'message': message
    }
    return (jsonify(error), staus_code)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()

            jwt.decode(token, JWT_SECRET_KEY)
        except AuthError as ex:
            return jsonify_error(ex.error, ex.status_code)
        except Exception as ex:
            print(ex)
            return jsonify_error("Unauthorized", 403)

        return f(*args, **kwargs)

    return decorated

def get_token_auth_header():
    """Obtains the access token from the Authorization Header"""

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError("Authorization header not found", 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError("Authorization header must start with Bearer", 401)
    elif len(parts) == 1:
        raise AuthError("Token not found", 401)
    elif len(parts) > 2:
        raise AuthError("Authorization header must be Bearer token", 401)

    token = parts[1]
    return token


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


def create_app(app_config=None):
    """Create and configure an instance of the Flask application."""

    FLASK_SECRET_KEY = env.get('FLASK_SECRET_KEY')
    if not FLASK_SECRET_KEY:
        FLASK_SECRET_KEY = "secretdev"

    global AUTH0_CALLBACK_URL, AUTH0_AUDIENCE, AUTH0_BASE_URL, AUTH0_CLIENT_SECRET, AUTH0_CLIENT_ID

    AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
    AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
    AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
    AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
    AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
    AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
    if AUTH0_AUDIENCE is '':
        AUTH0_AUDIENCE = AUTH0_BASE_URL + '/userinfo'
    
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY=FLASK_SECRET_KEY,
    )


    oauth = OAuth(app)
    global auth0 
    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile',
        },
    )

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)
    
@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/listings')

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/logout?' + urlencode(params))


@app.route('/')
@app.route('/home')
def home():
    if session and session[constants.PROFILE_KEY]:
        user_info_json = session[constants.JWT_PAYLOAD]
        user_id_string = user_info_json.get('sub', '0|0')
        user_id = user_id_string.split('|')[1]
        return render_template('home.html', userinfo=session[constants.PROFILE_KEY], userid=user_id)
    else:
        return render_template('home.html')






############



#app = Flask(__name__)
create_app()
client = MongoClient()

db = client['abnb']
reviews = db['reviews']
home_listings = db['listings']
calendar = db['calendar']


@app.route("/listings")
@requires_auth
def listings():
    rows = []
    for document in home_listings.find({}):
        temprow = []
        temprow.append(document["picture_url"])
        temprow.append(document["name"])
        temprow.append(document["price"])
        temprow.append(document["street"])
        temprow.append(document["id"])
        rows.append(temprow)
    rows.pop(0)
    user_id = session[constants.JWT_PAYLOAD].get('sub', '0|0').split("|")[1]
    return render_template("listings.html", rows=rows, userinfo=session[constants.PROFILE_KEY], userid=user_id)


@app.route("/listings/<listing_id>")
@requires_auth
def listing_details(listing_id):
    home = home_listings.find({"id" : int(listing_id) })[0]
    row = []
    headers = []
    excluded = ["", "N/A", "_id"]
    imageheaders = []
    images = []
    for key in home.keys():
        if "http" in str(home[key]) and (key!="host_url" and key!="listing_url"):
            imageheaders.append(key)
            images.append(home[key])
        elif not(str(home[key]) in excluded or key in excluded) and str(home[key]) not in row:
            headers.append(key)
            row.append(str(home[key]))
    return render_template("listing_details.html", imageheaders=imageheaders, headers=headers, images=images, row=row)

if __name__ == '__main__':
    app.run(debug=True)