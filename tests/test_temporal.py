from faceguard.temporal import TemporalVote


def test_requires_repeated_identity():
    vote = TemporalVote(window=5, required=3)
    assert vote.update("Ana") is None
    assert vote.update(None) is None
    assert vote.update("Ana") is None
    assert vote.update("Ana") == "Ana"


