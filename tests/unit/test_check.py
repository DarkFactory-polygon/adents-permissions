from datetime import date

from agentperm.check import decide
from agentperm.record import Record

TODAY = date(2026, 11, 23)


def r(number, until, agent="a", action="read", resource="x", by="alice"):
    return Record(agent, resource, action, by, until, number, number)


def test_valid():
    d = decide([r(1, TODAY)], "a", "read", "x", TODAY)
    assert d.allowed and d.record.number == 1


def test_expired_and_missing():
    recs = [r(1, date(2026, 11, 22))]
    d = decide(recs, "a", "read", "x", TODAY)
    assert not d.allowed and d.expired
    d = decide(recs, "a", "write", "x", TODAY)
    assert not d.allowed and not d.expired


def test_earliest_then_lowest_number():
    recs = [r(1, date(2027, 1, 1)), r(2, date(2026, 12, 1), by="b"), r(3, date(2026, 12, 1))]
    assert decide(recs, "a", "read", "x", TODAY).record.number == 2


def test_literal_and_case():
    recs = [r(1, date(2099, 1, 1), agent="*", resource="*", action="*"), r(2, date(2099, 1, 1), agent="Build-Bot")]
    assert decide(recs, "*", "*", "*", TODAY).allowed
    assert not decide(recs, "x", "*", "*", TODAY).allowed
    assert not decide(recs, "build-bot", "read", "x", TODAY).allowed
    assert not decide(recs, "Build-Bot ", "read", "x", TODAY).allowed
