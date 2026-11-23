from ._helpers import rec, write


def allowed(p):
    return p.returncode == 0 and "разрешено" in p.stdout.replace("запрещено", "")


def test_asterisk_is_literal_not_wildcard(run, tmp_path):
    write(tmp_path, rec(agent="'*'", resource="'*'", action="'*'"))
    assert allowed(run("check", "*", "*", "*"))
    for q in (("build-bot", "read", "repo/app"), ("*", "read", "*"), ("*", "*", "x")):
        p = run("check", *q)
        assert p.returncode == 1 and not allowed(p)


def test_case_and_edge_whitespace_are_significant(run, tmp_path):
    write(tmp_path, rec(agent="Build-Bot"))
    assert allowed(run("check", "Build-Bot", "read", "repo/app"))
    for agent in ("build-bot", "Build-Bot ", " Build-Bot"):
        p = run("check", agent, "read", "repo/app")
        assert p.returncode == 1 and not allowed(p)
