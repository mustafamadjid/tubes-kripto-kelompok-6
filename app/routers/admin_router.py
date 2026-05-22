from fastapi import APIRouter, Depends, Request
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
