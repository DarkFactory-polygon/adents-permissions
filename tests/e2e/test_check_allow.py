from datetime import date

from ._helpers import rec, write

Q = ("check", "build-bot", "read", "repo/app")


def test_valid_record_prints_grantor_and_until_exit_0(run, tmp_path):
    write(tmp_path, rec(by="carol", until="2099-05-06"))
    p = run(*Q)
    assert p.returncode == 0
    assert "разрешено" in p.stdout and "carol" in p.stdout and "2099-05-06" in p.stdout


def test_last_day_inclusive_allows(run, tmp_path):
    write(tmp_path, rec(until=date.today().isoformat()))
    p = run(*Q)
    assert p.returncode == 0 and "разрешено" in p.stdout


def test_one_valid_among_expired_wins(run, tmp_path):
    write(tmp_path, rec(by="old", until="2000-01-01"), rec(by="fresh", until="2099-02-03"))
    p = run(*Q)
    assert p.returncode == 0
    assert "fresh" in p.stdout and "2099-02-03" in p.stdout and "old" not in p.stdout
    assert run(*Q).stdout == p.stdout
