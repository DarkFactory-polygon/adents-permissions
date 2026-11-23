import os
import stat

import pytest

from .conftest import COMMANDS, combined

BAD_CASES = {
    "broken-yaml": "permissions: [unclosed\n  - : :\n",
    "no-key": "other: []\n",
    "not-list": "permissions: 5\n",
    "item-not-mapping": "permissions:\n  - just-a-string\n",
    "empty-file": "",
    "second-document": "permissions: []\n---\npermissions: []\n",
}


def assert_single_error(proc, path):
    out = combined(proc)
    assert proc.returncode == 2
    assert len(out.strip().splitlines()) == 1
    assert str(path) in out
    for banned in (
        "Traceback",
        'File "',
        "разрешено",
        "запрещено",
        "Просроченные",
        "Истекающие",
    ):
        assert banned not in out


@pytest.mark.parametrize("command", COMMANDS, ids=["check", "expired"])
@pytest.mark.parametrize("name", BAD_CASES)
def test_broken_yaml_single_line_error_exit_2(run, tmp_path, name, command):
    path = tmp_path / "permissions.yaml"
    path.write_text(BAD_CASES[name])
    proc = run(*command, "--file", str(path))
    assert_single_error(proc, path)


@pytest.mark.parametrize("command", COMMANDS, ids=["check", "expired"])
def test_missing_file_names_expected_path_exit_2(run, tmp_path, command):
    explicit = tmp_path / "nope" / "x.yaml"
    proc = run(*command, "--file", str(explicit))
    assert_single_error(proc, explicit)
    proc = run(*command)  # по умолчанию — permissions.yaml в рабочем каталоге
    assert_single_error(proc, "permissions.yaml")


@pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="нужен непривилегированный пользователь",
)
@pytest.mark.parametrize("command", COMMANDS, ids=["check", "expired"])
def test_unreadable_file_never_allows(run, tmp_path, command):
    path = tmp_path / "permissions.yaml"
    path.write_text(
        "permissions:\n- {agent: build-bot, resource: repo/app, action: read,"
        " granted_by: alice, until: 2099-01-01}\n"
    )
    path.chmod(0)
    try:
        proc = run(*command, "--file", str(path))
    finally:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    assert_single_error(proc, path)
    assert "не читается" in combined(proc)


@pytest.mark.parametrize("command", COMMANDS, ids=["check", "expired"])
def test_empty_permissions_list_is_valid(run, tmp_path, command):
    path = tmp_path / "permissions.yaml"
    path.write_text("permissions: []\n")
    proc = run(*command, "--file", str(path))
    assert proc.returncode in (0, 1)
    assert "ошибка" not in combined(proc)


def test_no_side_effects(run, tmp_path):
    path = tmp_path / "permissions.yaml"
    path.write_text("permissions: []\n")
    before = (path.read_bytes(), path.stat().st_mtime_ns, sorted(os.listdir(tmp_path)))
    run("expired")
    run("check", "a", "b", "c")
    run("expired", "--file", str(tmp_path / "missing.yaml"))
    after = (path.read_bytes(), path.stat().st_mtime_ns, sorted(os.listdir(tmp_path)))
    assert before == after
