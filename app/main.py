from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import admin_router, auth_router, voter_router

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(voter_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
