from flask import Flask, redirect, url_for, render_template, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
from dotenv import load_dotenv
import requests

API_ENDPOINT = 'http://167.71.54.75:8082/'
app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
oauth = OAuth(app)

load_dotenv()
# OAuth 2 client setup
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration")
print(GOOGLE_CLIENT_ID)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=GOOGLE_DISCOVERY_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.route('/')
def index():
    return 'You are not logged in.'


@app.route('/login')
def login():
    # put a url with an https here
    redirect_uri = "https://learn.techcamp.co.ke/login/callback"
    print(redirect_uri)
    session["nonce"] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])


@app.route("/login/callback")
def callback():
    token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(token, nonce=session["nonce"])
    email = google_user['email']
    full_name = google_user['name']

    # Fetch all trainees
    response = requests.get(f"{API_ENDPOINT}trainees")
    if response.status_code != 200:
        return "Error fetching trainees from external API", 500
    trainees = response.json()

    # Check if email exists in the list of trainees
    user = next(
        (trainee for trainee in trainees if trainee['email'] == email), None)
    if user:
        return user
    else:
        return user


if __name__ == "__main__":
    app.run(debug=True)
