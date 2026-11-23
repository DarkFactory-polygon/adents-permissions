import pytest

from .conftest import COMMANDS, combined

GOOD = "{agent: build-bot, resource: repo/app, action: read, granted_by: alice, until: 2099-01-01}"
IDS = ["check", "expired"]


def write(tmp_path, body):
    path = tmp_path / "permissions.yaml"
    path.write_text("permissions:\n" + body)
    return path


def assert_error(proc, path, *needles):
    out = combined(proc)
    assert proc.returncode == 2
    assert len(out.strip().splitlines()) == 1
    assert str(path) in out
    for needle in needles:
        assert needle in out
    for banned in ("Traceback", "разрешено", "Просроченные", "Истекающие"):
        assert banned not in out


def rec(**over):
    fields = {
        "agent": "build-bot",
        "resource": "repo/app",
        "action": "read",
        "granted_by": "alice",
        "until": "2099-01-01",
    }
    fields.update(over)
    items = [f"{k}: {v}" for k, v in fields.items() if v is not None]
    return "  - {" + ", ".join(items) + "}\n"


@pytest.mark.parametrize("command", COMMANDS, ids=IDS)
@pytest.mark.parametrize("field", ["agent", "resource", "action", "granted_by"])
@pytest.mark.parametrize("empty", [None, "''", '""', ""])
def test_missing_or_empty_field_is_an_error(run, tmp_path, command, field, empty):
    path = write(tmp_path, rec(**{field: empty}))
    proc = run(*command, "--file", str(path))
    assert_error(proc, path, field, "запись 1", "строка 2")


@pytest.mark.parametrize("command", COMMANDS, ids=IDS)
@pytest.mark.parametrize(
    "until",
    [None, "''", "30.11.2026", "2026-13-01", "2026-02-30", "2026-11-30T10:00:00",
     "2026-11-30+03:00", "завтра", "20261130"],
)
def test_invalid_or_absent_end_date_is_an_error(run, tmp_path, command, until):
    path = write(tmp_path, rec(until=until))
    proc = run(*command, "--file", str(path))
    assert_error(proc, path, "until", "запись 1")


@pytest.mark.parametrize("command", COMMANDS, ids=IDS)
def test_extra_field_and_duplicate_key_are_errors(run, tmp_path, command):
    path = write(tmp_path, rec(color="red"))
    assert_error(run(*command, "--file", str(path)), path, "color", "запись 1")
    path = write(tmp_path, rec(until="2099-01-01") .replace("}", ", agent: other}"))
    assert_error(run(*command, "--file", str(path)), path, "agent", "запись 1")


@pytest.mark.parametrize("command", COMMANDS, ids=IDS)
def test_single_bad_record_blocks_both_commands(run, tmp_path, command):
    path = write(tmp_path, rec() + rec(until="завтра") + rec())
    assert_error(run(*command, "--file", str(path)), path, "запись 2", "until")


@pytest.mark.parametrize("command", COMMANDS, ids=IDS)
def test_scalar_text_values_are_accepted(run, tmp_path, command):
    body = rec(agent="no", resource="'null'", action="~", granted_by="0007", until="'2099-01-01'")
    path = write(tmp_path, body)
    assert "ошибка" not in combined(run(*command, "--file", str(path)))
