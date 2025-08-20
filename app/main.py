from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# 🔑 Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecret"))

oauth = OAuth()

# Register the Google client
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    redirect_uri="http://127.0.0.1:8000/auth",  # Set a specific redirect URI
    client_kwargs={"scope": "openid profile email"},
)


@app.get("/login")
async def login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth"  # Explicit redirect URI
    authorization_url = await oauth.google.authorize_redirect(request, redirect_uri)
    return authorization_url


# callback route
@app.route("/auth")
async def auth(request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return JSONResponse(content={"user": user})
