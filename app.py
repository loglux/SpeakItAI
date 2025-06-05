from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import gradio as gr

from gradio_ui import demo
from backend.auth import login_router, init_db, get_current_user

import os
from dotenv import load_dotenv
load_dotenv()
SESSION_SECRET = os.getenv("SESSION_SECRET", "change_me_in_production")

# Creating the FastAPI application.
fastapi_app = FastAPI()

# Adding session middleware.
fastapi_app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="session",
    max_age=60 * 60 * 24
)

# Authentication routes.
fastapi_app.include_router(login_router)

# Database initialization on startup.
@fastapi_app.on_event("startup")
def startup_event():
    init_db()

# First launch
@fastapi_app.get("/", response_class=RedirectResponse)
def root():
    from backend.auth import users_exist
    if not users_exist():
        return RedirectResponse("/register")
    return RedirectResponse("/tts")


# Redirect from the root.
@fastapi_app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse("/tts")

# Now mounting the Gradio interface.
app = gr.mount_gradio_app(fastapi_app, demo, path="/tts",  auth_dependency=get_current_user)
