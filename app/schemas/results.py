from dataclasses import dataclass, field


@dataclass(frozen=True)
class VoteCastResult:
    voter_id: str
    candidate_id: int
    vote_record_id: str


@dataclass(frozen=True)
class CandidateVoteResult:
    candidate_id: int
    candidate_name: str
    vote_count: int


@dataclass(frozen=True)
class InvalidVoteDetail:
    vote_id: str
    voter_id: str
    status: str
    reason: str


@dataclass(frozen=True)
class RecapitulationResult:
    total_votes: int
    valid_votes: int
    invalid_votes: int
    candidate_results: list[CandidateVoteResult] = field(default_factory=list)
    invalid_vote_details: list[InvalidVoteDetail] = field(default_factory=list)


@dataclass(frozen=True)
class BenchmarkResult:
    operation_name: str
    duration_ms: float
