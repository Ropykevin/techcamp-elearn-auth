from flask import Flask, redirect, url_for, render_template, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
from dotenv import load_dotenv

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
    redirect_uri = ""  # put a url with an https here
    print(redirect_uri)
    session["nonce"] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])


@app.route("/login/callback")
def callback():
    token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(token, nonce=session["nonce"])
    return google_user['email']


if __name__ == "__main__":
    app.run(debug=True)
