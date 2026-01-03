from flask import Flask, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth
import json
import os
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "super-secret-dev-key" # Wenn die App neu startest, ändert sich der Key → bestehende Sessions sind damit ungültig. Ggf. später Key fest speichern, z. B. über eine Umgebungsvariable oder .env Datei.

AUTH0_CLIENT_ID = "PSUK1RaIxvq378ykE1whyNNuu9gMHyU4"
AUTH0_CLIENT_SECRET = "UOID8dYPW28eYjuAuITSBylejjJadKqnV4VzVa0S3I15DveK1CbePhPHKb8l90G-"
AUTH0_DOMAIN = "dev-dzpxx3scxsebbgz0.us.auth0.com"
AUTH0_CALLBACK_URL = "http://localhost:5001/callback"

oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    userinfo = token.get("userinfo")  
    if not userinfo: 
        userinfo = auth0.userinfo()  
    with open("auth0_result.json", "w") as f:
        json.dump(userinfo, f)
    return "✅ Login successful, you can close this window."


if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5001")).start()
    app.run(port=5001)