"""Проверка записи: пятёрка полей, значения как исходный текст скаляра (DEL-13)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import yaml

from agentperm.errors import RegistryError

FIELDS = ("agent", "resource", "action", "granted_by", "until")
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


@dataclass(frozen=True)
class Record:
    agent: str
    resource: str
    action: str
    granted_by: str
    until: date
    line: int
    number: int


def parse_until(text: str) -> date | None:
    """ГГГГ-ММ-ДД с существующей календарной датой, иначе None."""
    if not _DATE_RE.fullmatch(text):
        return None
    try:
        return date(int(text[:4]), int(text[5:7]), int(text[8:10]))
    except ValueError:
        return None


def build_record(node: yaml.MappingNode, number: int, path: str) -> Record:
    """Превратить узел записи в Record или бросить RegistryError."""
    line = node.start_mark.line + 1

    def fail(what: str, field: str | None = None, at: int = line) -> RegistryError:
        return RegistryError(what, path, at, number, field)

    values: dict[str, str] = {}
    for key_node, val_node in node.value:
        key_line = key_node.start_mark.line + 1
        if not isinstance(key_node, yaml.ScalarNode):
            raise fail("ключ поля не является строкой", None, key_line)
        key = key_node.value
        if key not in FIELDS:
            raise fail(f"лишнее поле {key!r}", key, key_line)
        if key in values:
            raise fail(f"поле {key} задано дважды", key, key_line)
        if not isinstance(val_node, yaml.ScalarNode):
            raise fail(f"значение поля {key} не скаляр", key, key_line)
        values[key] = val_node.value  # исходный текст, без разрешения типов

    for name in FIELDS:
        if name not in values:
            raise fail(f"нет поля {name}", name)
        if values[name] == "":
            raise fail(f"пустое поле {name}", name)

    until = parse_until(values["until"])
    if until is None:
        raise fail(
            f"поле until должно быть датой ГГГГ-ММ-ДД, получено {values['until']!r}",
            "until",
        )
    return Record(
        values["agent"],
        values["resource"],
        values["action"],
        values["granted_by"],
        until,
        line,
        number,
    )
