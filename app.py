from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import gradio as gr

from gradio_ui import demo
from backend.auth import login_router, init_db, get_current_user

# Создание приложения FastAPI
fastapi_app = FastAPI()

# Добавляем middleware для сессий
fastapi_app.add_middleware(
    SessionMiddleware,
    secret_key="b7f8a22e6d9c49dfb38dfc3f34b3a5e5f9a34a8b23c64e1a0e6e71b90d2b9c51",
    session_cookie="session",
    max_age=60 * 60 * 24
)

# Роуты авторизации
fastapi_app.include_router(login_router)

# Инициализация базы при запуске
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


# Редирект с корня
@fastapi_app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse("/tts")

# # Защищённый доступ к Gradio UI
# @fastapi_app.get("/gradio")
# def protected_gradio(request: Request, user: str = Depends(get_current_user)):
#     return RedirectResponse("/gradio_ui")

# @fastapi_app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse("/", status_code=302)

# Теперь монтируем Gradio интерфейс
app = gr.mount_gradio_app(fastapi_app, demo, path="/tts",  auth_dependency=get_current_user)
