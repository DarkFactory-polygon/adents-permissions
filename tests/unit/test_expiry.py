from datetime import date

from agentperm.check import split_expiry
from agentperm.record import Record


def r(n, until):
    return Record("a", "r", "x", "g", date.fromisoformat(until), n, n)


def test_split_boundaries_and_order():
    today = date(2026, 11, 23)
    recs = [r(1, "2026-11-30"), r(2, "2026-11-22"), r(3, "2026-11-23"), r(4, "2026-12-01"), r(5, "2026-11-22")]
    over, soon = split_expiry(recs, today)
    assert [x.number for x in over] == [2, 5]
    assert [x.number for x in soon] == [3, 1]
