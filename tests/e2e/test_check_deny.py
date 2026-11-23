from ._helpers import rec, write

Q = ("check", "build-bot", "read", "repo/app")


def test_expired_record_denies_exit_1(run, tmp_path):
    write(tmp_path, rec(until="2000-01-01"), rec(until="2001-01-01"))
    p = run(*Q)
    assert p.returncode == 1
    assert "запрещено" in p.stdout and "срок истёк" in p.stdout
    assert "разрешено" not in p.stdout.replace("запрещено", "")


def test_no_record_denies_exit_1(run, tmp_path):
    write(tmp_path, rec(action="write"))
    p = run(*Q)
    assert p.returncode == 1
    assert "запрещено" in p.stdout and "записи нет" in p.stdout
    assert "разрешено" not in p.stdout.replace("запрещено", "")
