from ._helpers import rec, write

H1 = "Просроченные:"
H2 = "Истекающие в ближайшие 7 дней:"


def sections(out):
    lines = out.splitlines()
    i = lines.index(H1)
    j = lines.index(H2)
    assert i < j
    return lines[i + 1 : j], lines[j + 1 :]


def test_group_boundaries_on_2026_11_23(run, tmp_path):
    dates = ["2026-11-21", "2026-11-22", "2026-11-23", "2026-11-30", "2026-12-01"]
    write(tmp_path, *[rec(agent=f"a{i}", until=d) for i, d in enumerate(dates)])
    p = run("expired")
    over, soon = sections(p.stdout)
    assert [("until=" + d in " ".join(over)) for d in dates[:2]] == [True, True]
    assert len(over) == 2
    assert len(soon) == 2
    assert "until=2026-11-23" in soon[0] and "until=2026-11-30" in soon[1]
    assert "2026-12-01" not in p.stdout


def test_each_row_has_all_five_fields(run, tmp_path):
    write(tmp_path, rec(agent="ag", resource="res", action="act", by="bob", until="2026-11-25"))
    p = run("expired")
    _, soon = sections(p.stdout)
    for v in ("ag", "res", "act", "bob", "2026-11-25"):
        assert v in soon[0]


def test_duplicate_right_yields_two_rows(run, tmp_path):
    write(tmp_path, rec(until="2026-11-25"), rec(until="2026-11-25"))
    _, soon = sections(run("expired").stdout)
    assert len(soon) == 2 and soon[0] == soon[1]


def test_order_by_date_then_number(run, tmp_path):
    write(
        tmp_path,
        rec(agent="c", until="2026-11-27"),
        rec(agent="a", until="2026-11-24"),
        rec(agent="b", until="2026-11-24"),
    )
    _, soon = sections(run("expired").stdout)
    assert [r.split()[0] for r in soon] == ["agent=a", "agent=b", "agent=c"]


def test_exit_code_zero_for_empty_and_nonempty_groups(run, tmp_path):
    write(tmp_path, rec(until="2099-01-01"))
    p = run("expired")
    assert p.returncode == 0
    assert sections(p.stdout) == ([], [])
    write(tmp_path, rec(until="2000-01-01"), rec(until="2026-11-24"))
    p = run("expired")
    assert p.returncode == 0
    over, soon = sections(p.stdout)
    assert len(over) == 1 and len(soon) == 1
