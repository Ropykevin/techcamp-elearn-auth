from flask import Flask, redirect, url_for, render_template, session, make_response
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
oauth = OAuth(app)

API_ENDPOINT = 'http://167.71.54.75:8082/trainees/'
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
    response = requests.get(f"{API_ENDPOINT}?email={email}")
    if response.status_code == 200 and response.json():
        user = response.json()
        return f"Hello, {user['fullName']}! You have logged in successfully."
    else:
        payload = {
            "email": email,
            "firebaseId": 'web',
            "fullName": full_name,
            "id": 0,
            "latestDeviceId": "web"
        }
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 201:
            return "Error storing user in external API", 500
        user = response.json()
        # Set cookies with user information
        response = make_response(
            f"Hello, {user['fullName']}! You have been registered and logged in successfully.")
        response.set_cookie('user_email', email)
        response.set_cookie('user_full_name', full_name)
        return response

if __name__ == "__main__":
    app.run(debug=True)
