import pytest

from agentperm.cli import main
from agentperm.errors import RegistryError
from agentperm.loader import load_records


def test_valid_records(tmp_path):
    p = tmp_path / "p.yaml"
    p.write_text("permissions:\n  - {agent: a, resource: r, action: x, granted_by: g, until: 2030-01-01}\n  - {agent: b, resource: r, action: x, granted_by: g, until: 2030-01-01}\n")
    assert len(load_records(str(p))) == 2


def test_error_render_has_pointers():
    text = RegistryError("плохо", "f.yaml", 3, 2, "until").render()
    assert text == "ошибка: плохо: f.yaml: строка 3, запись 2, поле until"


def test_duplicate_top_key_and_extra_key(tmp_path):
    p = tmp_path / "p.yaml"
    p.write_text("permissions: []\npermissions: []\n")
    with pytest.raises(RegistryError):
        load_records(str(p))
    p.write_text("permissions: []\nextra: 1\n")
    with pytest.raises(RegistryError):
        load_records(str(p))


def test_non_mapping_root_and_bad_utf8(tmp_path):
    p = tmp_path / "p.yaml"
    p.write_text("- 1\n")
    with pytest.raises(RegistryError):
        load_records(str(p))
    p.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(RegistryError):
        load_records(str(p))


def test_directory_is_unreadable(tmp_path):
    with pytest.raises(RegistryError, match="не читается"):
        load_records(str(tmp_path))


def test_main_internal_error_is_one_line(monkeypatch, capsys):
    def boom(_):
        raise ValueError("x")

    monkeypatch.setattr("agentperm.cli.load_records", boom)
    assert main(["expired"]) == 2
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1 and "Traceback" not in err


def test_empty_registry_codes(tmp_path, capsys):
    p = tmp_path / "p.yaml"
    p.write_text("permissions: []\n")
    assert main(["expired", "--file", str(p)]) == 0
    assert main(["check", "a", "b", "c", "--file", str(p)]) == 1


def _rec(text):
    import yaml

    from agentperm.record import build_record

    return build_record(yaml.compose(text), 1, "f.yaml")


def test_scalars_keep_source_text():
    r = _rec(
        "{agent: no, resource: 'null', action: '~', granted_by: 0007, until: '2030-01-01'}"
    )
    assert (r.agent, r.resource, r.action, r.granted_by) == ("no", "null", "~", "0007")
    assert str(r.until) == "2030-01-01"


@pytest.mark.parametrize(
    "text",
    [
        "{agent: [a], resource: r, action: x, granted_by: g, until: 2030-01-01}",
        "{[a]: 1, resource: r, action: x, granted_by: g, until: 2030-01-01}",
        "{agent: a, agent: b, resource: r, action: x, granted_by: g, until: 2030-01-01}",
        "{agent: a, resource: r, action: x, granted_by: g, until: 2030-01-01, z: 1}",
        "{agent: a, resource: r, action: x, granted_by: g}",
        "{agent: '', resource: r, action: x, granted_by: g, until: 2030-01-01}",
        "{agent: a, resource: r, action: x, granted_by: g, until: 0000-01-01}",
    ],
)
def test_bad_records(text):
    with pytest.raises(RegistryError):
        _rec(text)
