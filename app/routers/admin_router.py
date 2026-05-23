"""HTTP routers."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.benchmark_repository import BenchmarkRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.vote_repository import VoteRepository
from app.repositories.voter_repository import VoterRepository
from app.services.factory import create_recapitulation_service

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse("/admin/login", status_code=303)
    return None


# ── Dashboard ──────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    context = {
        "request": request,
        "total_voters": VoterRepository(db).count_all(),
        "total_candidates": CandidateRepository(db).count_all(),
        "total_votes": VoteRepository(db).count_all(),
        "total_audit_logs": AuditLogRepository(db).count_all(),
    }
    return templates.TemplateResponse(request, "admin_dashboard.html", context)


# ── Recapitulation & Results ───────────────────────────────────────────────────

@router.post("/recapitulate")
def recapitulate(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    result = create_recapitulation_service(db).recapitulate_votes()
    db.commit()
    request.session["latest_recap"] = {
        "total_votes": result.total_votes,
        "valid_votes": result.valid_votes,
        "invalid_votes": result.invalid_votes,
        "candidate_results": [item.__dict__ for item in result.candidate_results],
        "invalid_vote_details": [item.__dict__ for item in result.invalid_vote_details],
    }
    return RedirectResponse("/admin/results", status_code=303)


@router.get("/results")
def results(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(request, "recap_result.html", {"result": request.session.get("latest_recap")})


# ── Audit & Benchmarks ─────────────────────────────────────────────────────────

@router.get("/audit-logs")
def audit_logs(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(request, "audit_logs.html", {"logs": AuditLogRepository(db).find_all()})


@router.get("/benchmarks")
def benchmarks(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(request, "benchmark.html", {"records": BenchmarkRepository(db).find_all()})


# ── Candidates CRUD ────────────────────────────────────────────────────────────

@router.get("/candidates")
def candidates_list(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    candidates = CandidateRepository(db).find_all()
    flash = request.session.pop("flash", None)
    return templates.TemplateResponse(request, "admin_candidates.html", {
        "candidates": candidates,
        "flash": flash,
    })


@router.post("/candidates/create")
def candidates_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect:
        return redirect
    name = name.strip()
    if not name:
        request.session["flash"] = {"type": "error", "msg": "Nama kandidat tidak boleh kosong."}
        return RedirectResponse("/admin/candidates", status_code=303)
    CandidateRepository(db).create(name=name, description=description.strip() or None)
    db.commit()
    request.session["flash"] = {"type": "success", "msg": f"Kandidat '{name}' berhasil ditambahkan."}
    return RedirectResponse("/admin/candidates", status_code=303)


@router.get("/candidates/{candidate_id}/edit")
def candidates_edit_page(candidate_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    candidate = CandidateRepository(db).find_by_id(candidate_id)
    if candidate is None:
        request.session["flash"] = {"type": "error", "msg": "Kandidat tidak ditemukan."}
        return RedirectResponse("/admin/candidates", status_code=303)
    return templates.TemplateResponse(request, "admin_candidate_edit.html", {"candidate": candidate})


@router.post("/candidates/{candidate_id}/edit")
def candidates_edit(
    candidate_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect:
        return redirect
    name = name.strip()
    if not name:
        request.session["flash"] = {"type": "error", "msg": "Nama kandidat tidak boleh kosong."}
        return RedirectResponse(f"/admin/candidates/{candidate_id}/edit", status_code=303)
    updated = CandidateRepository(db).update(candidate_id, name=name, description=description.strip() or None)
    if updated is None:
        request.session["flash"] = {"type": "error", "msg": "Kandidat tidak ditemukan."}
    else:
        db.commit()
        request.session["flash"] = {"type": "success", "msg": f"Kandidat '{name}' berhasil diperbarui."}
    return RedirectResponse("/admin/candidates", status_code=303)


@router.post("/candidates/{candidate_id}/delete")
def candidates_delete(candidate_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request)
    if redirect:
        return redirect
    repo = CandidateRepository(db)
    candidate = repo.find_by_id(candidate_id)
    name = candidate.name if candidate else "?"
    deleted = repo.delete(candidate_id)
    if deleted:
        db.commit()
        request.session["flash"] = {"type": "success", "msg": f"Kandidat '{name}' berhasil dihapus."}
    else:
        request.session["flash"] = {"type": "error", "msg": "Kandidat tidak ditemukan."}
    return RedirectResponse("/admin/candidates", status_code=303)
