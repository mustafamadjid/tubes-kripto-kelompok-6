from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.exceptions import CandidateNotFoundError, VoterAlreadyVotedError, VoterNotFoundError
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.voter_repository import VoterRepository
from app.services.factory import create_voting_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def root():
    return RedirectResponse("/login", status_code=303)


@router.get("/vote")
def vote_page(request: Request, db: Session = Depends(get_db)):
    voter_id = request.session.get("voter_id")
    if not voter_id:
        return RedirectResponse("/login", status_code=303)
    voter = VoterRepository(db).find_by_voter_id(voter_id)
    if voter is None:
        return RedirectResponse("/login", status_code=303)
    candidates = CandidateRepository(db).find_all()
    return templates.TemplateResponse(request, "vote.html", {"voter": voter, "candidates": candidates})


@router.post("/vote")
def cast_vote(request: Request, candidate_id: int = Form(...), db: Session = Depends(get_db)):
    voter_id = request.session.get("voter_id")
    if not voter_id:
        return RedirectResponse("/login", status_code=303)
    try:
        result = create_voting_service(db).cast_vote(voter_id, candidate_id)
        db.commit()
    except (VoterNotFoundError, VoterAlreadyVotedError, CandidateNotFoundError, FileNotFoundError) as exc:
        db.rollback()
        voter = VoterRepository(db).find_by_voter_id(voter_id)
        candidates = CandidateRepository(db).find_all()
        return templates.TemplateResponse(
            request,
            "vote.html",
            {"voter": voter, "candidates": candidates, "error": str(exc)},
        )
    return RedirectResponse(f"/vote/success?vote_id={result.vote_record_id}", status_code=303)


@router.get("/vote/success")
def vote_success(request: Request, vote_id: str | None = None):
    return templates.TemplateResponse(request, "vote_success.html", {"vote_id": vote_id})
