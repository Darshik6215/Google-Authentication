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

# Register the Google client with explicit endpoints
try:
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",  # Explicit JWKS URI for Google
        issuer="https://accounts.google.com",  # For OpenID Connect context
        client_kwargs={"scope": "openid profile email"},  # Ensure openid is included
        redirect_uri="http://127.0.0.1:8000/auth",  # Match this with Google Console
    )
    print("OAuth client registered successfully:", oauth.google is not None)
except Exception as e:
    print(f"Failed to register OAuth client: {e}")

# Debug the registered client
print("OAuth client:", oauth.google)  # Check if the client is None


@app.get("/login")
async def login(request: Request):
    if oauth.google is None:
        return JSONResponse(
            content={"error": "Google OAuth client not initialized"}, status_code=500
        )
    redirect_uri = "http://127.0.0.1:8000/auth"  # Explicit redirect URI
    # Force consent to ensure id_token is issued
    try:
        authorization_url = await oauth.google.authorize_redirect(
            request, redirect_uri, prompt="consent"
        )
        return authorization_url
    except Exception as e:
        return JSONResponse(
            content={"error": f"Authorization failed: {str(e)}"}, status_code=500
        )


# callback route
@app.route("/auth")
async def auth(request: Request):
    if oauth.google is None:
        return JSONResponse(
            content={"error": "Google OAuth client not initialized"}, status_code=500
        )
    try:
        token = await oauth.google.authorize_access_token(request)
        print("Token response:", token)  # Debug the token response
        if "id_token" not in token:
            return JSONResponse(
                content={"error": "ID token not received from Google"}, status_code=400
            )
        id_token = token["id_token"]  # Extract the id_token string
        print("ID token:", id_token)  # Debug the id_token
        user = await oauth.google.parse_id_token(
            request, id_token
        )  # Pass the id_token string directly
        print("Parsed user:", user)  # Debug the parsed user data
        return JSONResponse(content={"user": user})
    except Exception as e:
        print(f"Authentication error: {str(e)}")  # Log the specific exception
        return JSONResponse(
            content={"error": f"Authentication failed: {str(e)}"}, status_code=500
        )


# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from authlib.integrations.starlette_client import OAuth
# from starlette.middleware.sessions import SessionMiddleware
# from dotenv import load_dotenv
# import os


# load_dotenv()

# app = FastAPI()


# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecret"))

# oauth = OAuth()


# oauth.register(
#     name="google",
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     authorize_url="https://accounts.google.com/o/oauth2/auth",
#     redirect_uri="http://127.0.0.1:8000/auth",
#     client_kwargs={"scope": "openid profile email"},
# )


# @app.get("/login")
# async def login(request: Request):
#     redirect_uri = "http://127.0.0.1:8000/auth"
#     authorization_url = await oauth.google.authorize_redirect(request, redirect_uri)
#     return authorization_url


# @app.route("/auth")
# async def auth(request):
#     token = await oauth.google.authorize_access_token(request)
#     user = await oauth.google.parse_id_token(request, token)
#     return JSONResponse(content={"user": user})
