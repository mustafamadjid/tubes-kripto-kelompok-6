"""Google OAuth router — menangani login via akun Google/kampus ITERA.

Dua mode operasi (set via OAUTH_MODE di .env):

  production  — hanya domain @student.itera.ac.id yang diizinkan.
                voter_id di-extract dari NIM 9 digit dalam email.
                Contoh: muhammad.123140148@student.itera.ac.id → voter_id = "123140148"

  demo        — domain bebas (atau sesuai ALLOWED_EMAIL_DOMAINS).
                voter_id = seluruh username sebelum @, titik diganti underscore.
                Contoh: budi.santoso@gmail.com → voter_id = "budi_santoso"
                Ini untuk simulasi presentasi tanpa perlu akun ITERA asli.
"""
import re
import secrets
from urllib.parse import urlencode

from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.repositories.voter_repository import VoterRepository

router = APIRouter(prefix="/auth/google")
templates = Jinja2Templates(directory="app/templates")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = "openid email profile"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _redirect_uri(role: str) -> str:
    return f"{settings.app_base_url}/auth/google/callback/{role}"


def _is_domain_allowed(email: str) -> bool:
    """Cek apakah domain email masuk dalam whitelist."""
    if not settings.allowed_email_domains.strip():
        return True  # kosong = semua domain boleh
    allowed = [d.strip().lower() for d in settings.allowed_email_domains.split(",")]
    domain = email.split("@")[-1].lower()
    return domain in allowed


def _is_admin_email(email: str) -> bool:
    if not settings.admin_google_emails.strip():
        return False
    allowed = [e.strip().lower() for e in settings.admin_google_emails.split(",")]
    return email.strip().lower() in allowed


def _extract_voter_id(email: str) -> tuple[str | None, str]:
    """
    Ekstrak voter_id dari email sesuai mode operasi.

    Returns:
        (voter_id, info_string)
        voter_id = None jika gagal extract di mode production.
    """
    username = email.split("@")[0]  # bagian sebelum @

    if settings.oauth_mode == "production":
        # Mode production: wajib ada NIM 9 digit
        match = re.search(r'(\d{9})', email)
        if not match:
            return None, f"Tidak dapat menemukan NIM 9 digit dalam email '{email}'."
        voter_id = match.group(1)
        return voter_id, f"NIM '{voter_id}' dari email '{email}'"

    else:
        # Mode demo: voter_id = username, titik → underscore
        # Contoh: budi.santoso@gmail.com → "budi_santoso"
        voter_id = username.replace(".", "_")
        return voter_id, f"voter_id '{voter_id}' dari email '{email}' (mode demo)"


# ─── Voter: mulai OAuth flow ───────────────────────────────────────────────────

@router.get("/voter")
async def voter_google_login(request: Request):
    if not settings.google_client_id:
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Google OAuth belum dikonfigurasi. Hubungi admin."}
        )
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": _redirect_uri("voter"),
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "prompt": "select_account",
    }
    # Hint domain hanya di mode production dengan satu domain
    if settings.oauth_mode == "production":
        domains = [d.strip() for d in settings.allowed_email_domains.split(",") if d.strip()]
        if len(domains) == 1:
            params["hd"] = domains[0]  # hint ke Google supaya langsung arahkan domain kampus

    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


# ─── Admin: mulai OAuth flow ───────────────────────────────────────────────────

@router.get("/admin")
async def admin_google_login(request: Request):
    if not settings.google_client_id:
        return templates.TemplateResponse(
            request, "admin_login.html",
            {"error": "Google OAuth belum dikonfigurasi. Hubungi admin."}
        )
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": _redirect_uri("admin"),
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


# ─── Callback ─────────────────────────────────────────────────────────────────

@router.get("/callback/{role}")
async def google_callback(role: str, request: Request, db: Session = Depends(get_db)):
    """Terima authorization code dari Google, tukar token, ambil info user."""

    # Validasi state (CSRF protection)
    state_in_session = request.session.pop("oauth_state", None)
    state_in_params = request.query_params.get("state")
    if not state_in_session or state_in_session != state_in_params:
        tpl = "login.html" if role == "voter" else "admin_login.html"
        return templates.TemplateResponse(request, tpl, {"error": "OAuth state tidak valid. Coba lagi."})

    code = request.query_params.get("code")
    if not code:
        error_msg = request.query_params.get("error", "Login dibatalkan.")
        tpl = "login.html" if role == "voter" else "admin_login.html"
        return templates.TemplateResponse(request, tpl, {"error": error_msg})

    # Tukar code → access token → userinfo
    async with AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    ) as client:
        token = await client.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            redirect_uri=_redirect_uri(role),
        )
        resp = await client.get(GOOGLE_USERINFO_URL, token=token)
        userinfo = resp.json()

    email: str = userinfo.get("email", "")
    name: str = userinfo.get("name", "")
    email_verified: bool = userinfo.get("email_verified", False)

    # Validasi email verified
    if not email or not email_verified:
        tpl = "login.html" if role == "voter" else "admin_login.html"
        return templates.TemplateResponse(request, tpl, {
            "error": "Email Google tidak terverifikasi. Gunakan akun resmi kampus."
        })

    # Validasi domain
    if not _is_domain_allowed(email):
        tpl = "login.html" if role == "voter" else "admin_login.html"
        mode_label = "production (kampus ITERA)" if settings.oauth_mode == "production" else "demo"
        return templates.TemplateResponse(request, tpl, {
            "error": (
                f"Email '{email}' tidak diizinkan di mode {mode_label}. "
                f"Domain yang diizinkan: {settings.allowed_email_domains or '(semua)'}"
            )
        })

    # ── ADMIN flow ─────────────────────────────────────────────────────────────
    if role == "admin":
        if not _is_admin_email(email):
            return templates.TemplateResponse(request, "admin_login.html", {
                "error": f"Email '{email}' tidak terdaftar sebagai admin Google."
            })
        request.session["is_admin"] = True
        request.session["admin_email"] = email
        request.session["admin_name"] = name
        return RedirectResponse("/admin/dashboard", status_code=303)

    # ── VOTER flow ─────────────────────────────────────────────────────────────
    voter_id, extract_info = _extract_voter_id(email)

    if voter_id is None:
        # Hanya terjadi di mode production jika NIM tidak ditemukan
        return templates.TemplateResponse(request, "login.html", {
            "error": (
                f"Tidak dapat mengekstrak NIM dari email '{email}'. "
                "Format email harus mengandung NIM 9 digit, "
                "contoh: muhammad.123140148@student.itera.ac.id"
            )
        })

    voter = VoterRepository(db).find_by_voter_id(voter_id)
    if voter is None:
        if settings.oauth_mode == "demo":
            hint = (
                f"Jalankan: python scripts/seed_data.py "
                f"(pastikan ada voter dengan voter_id='{voter_id}')"
            )
        else:
            hint = f"Pastikan NIM '{voter_id}' sudah didaftarkan admin di sistem."
        return templates.TemplateResponse(request, "login.html", {
            "error": f"{extract_info} tidak ditemukan di database. {hint}"
        })

    request.session["voter_id"] = voter.voter_id
    request.session["voter_email"] = email
    request.session["oauth_mode"] = settings.oauth_mode
    return RedirectResponse("/vote", status_code=303)
