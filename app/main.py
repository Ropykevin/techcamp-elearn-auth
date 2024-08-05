from flask import Flask, redirect, url_for, render_template, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Load the secret key from environment variable
app.secret_key = 'uuuuuuuuuuuuuu'
oauth = OAuth(app)

API_ENDPOINT = 'http://167.71.54.75:8082/trainees'

# OAuth 2 client setup
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=GOOGLE_DISCOVERY_URL,
    client_kwargs={'scope': 'openid email profile'}
)


@app.route('/')
def index():
    return 'You are not logged in.'


@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True, _scheme='https')
    session["nonce"] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])


@app.route("/login/callback")
def callback():
    token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(token, nonce=session["nonce"])
    email = google_user['email']
    full_name = google_user['name']

    # Fetch all trainees
    response = requests.get(API_ENDPOINT)
    if response.status_code != 200:
        return "Error fetching trainees from external API", 500
    trainees = response.json()

    # Check if email exists in the list of trainees
    user = next(
        (trainee for trainee in trainees if trainee['email'] == email), None)
    if user:
        return user
    else:
        # If user does not exist, create a new user
        payload = {
            "email": email,
            "firebaseId": "web",
            "fullName": full_name,
            "id": 0,
            "latestDeviceId": "web"
        }
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 201:
            return "Error storing user in external API", 500
        user = response.json()
        return user


if __name__ == "__main__":
    app.run(debug=True)
