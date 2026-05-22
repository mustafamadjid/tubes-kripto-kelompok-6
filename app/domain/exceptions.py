class VoterNotFoundError(Exception):
    pass


class VoterAlreadyVotedError(Exception):
    pass


class CandidateNotFoundError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


class HashMismatchError(Exception):
    pass


class VoteDecryptionError(Exception):
    pass


class MalformedVotePlaintextError(Exception):
    pass
