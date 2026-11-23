import pytest

from ._helpers import rec, write
from .conftest import combined


def test_file_option_and_default_path(run, tmp_path):
    write(tmp_path, rec(agent="default-bot"))
    other = tmp_path / "other.yaml"
    other.write_text("permissions:\n" + rec(agent="other-bot"))
    broken = tmp_path / "broken.yaml"
    broken.write_text("permissions: 5\n")

    proc = run("check", "default-bot", "read", "repo/app")
    assert proc.returncode == 0
    assert run("check", "other-bot", "read", "repo/app").returncode == 1

    proc = run("check", "other-bot", "read", "repo/app", "--file", str(other))
    assert proc.returncode == 0
    proc = run("check", "default-bot", "read", "repo/app", "--file", str(other))
    assert proc.returncode == 1

    proc = run("expired", "--file", str(broken))
    assert proc.returncode == 2
    assert str(broken) in combined(proc)

    sub = tmp_path / "sub"
    sub.mkdir()
    proc = run("expired", cwd=sub)
    assert proc.returncode == 2
    assert "permissions.yaml" in combined(proc)


BAD_CALLS = [
    ("grant", "a", "read", "r"),
    ("renew",),
    ("revoke",),
    ("import",),
    ("sync",),
    (),
    ("check", "a", "read"),
    ("check", "a", "read", "r", "extra"),
]


@pytest.mark.parametrize("call", BAD_CALLS)
def test_unknown_command_and_bad_arity_exit_2(run, tmp_path, call):
    outputs = []
    for state in ("good", "broken", "missing"):
        d = tmp_path / state
        d.mkdir()
        if state == "good":
            (d / "permissions.yaml").write_text("permissions:\n" + rec())
        elif state == "broken":
            (d / "permissions.yaml").write_text("permissions: [unclosed\n")
        proc = run(*call, cwd=d)
        assert proc.returncode == 2
        out = combined(proc)
        assert "check" in out and "expired" in out
        for banned in ("разрешено", "запрещено", "Просроченные", "Истекающие", "Traceback"):
            assert banned not in out
        for name in ("grant", "renew", "revoke", "import", "sync"):
            assert f"agentperm {name}" not in out
        outputs.append((proc.stdout, proc.stderr, proc.returncode))
    assert outputs[0] == outputs[1] == outputs[2]
