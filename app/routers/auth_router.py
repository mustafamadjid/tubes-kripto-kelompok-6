from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.voter_repository import VoterRepository
from app.services.auth_service import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
def login(request: Request, voter_id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    voter = AuthService(VoterRepository(db)).authenticate_voter(voter_id, password)
    if voter is None:
        return templates.TemplateResponse(request, "login.html", {"error": "Voter ID atau password salah."})
    request.session["voter_id"] = voter.voter_id
    return RedirectResponse("/vote", status_code=303)


@router.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin_login.html")


@router.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not AuthService().authenticate_admin(username, password):
        return templates.TemplateResponse(request, "admin_login.html", {"error": "Admin credential salah."})
    request.session["is_admin"] = True
    return RedirectResponse("/admin/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
