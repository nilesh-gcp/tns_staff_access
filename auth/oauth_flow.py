import requests
from urllib.parse import urlencode
from config.config import get

# Load credentials from [google_json] section in secrets.toml
CLIENT_ID = get("google_json", "GOOGLE_CLIENT_ID")
CLIENT_SECRET = get("google_json", "GOOGLE_CLIENT_SECRET")
REDIRECT_URI = get("google_json", "REDIRECT_URI")

# OAuth endpoints
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

def get_auth_url():
    """
    Builds the Google OAuth authorization URL.
    """
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"

def fetch_token(code):
    """
    Exchanges the authorization code for an access token.
    """
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    try:
        response = requests.post(TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error fetching token:", e)
        return {}

def get_user_info(access_token):
    """
    Retrieves user profile info using the access token.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(USERINFO_URL, headers=headers)
    return response.json()