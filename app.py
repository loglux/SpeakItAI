from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import gradio as gr

from gradio_ui import demo
from backend.auth import login_router, init_db, get_current_user

# Creating the FastAPI application.
fastapi_app = FastAPI()

# Adding session middleware.
fastapi_app.add_middleware(
    SessionMiddleware,
    secret_key="b7f8a22e6d9c49dfb38dfc3f34b3a5e5f9a34a8b23c64e1a0e6e71b90d2b9c51",
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
