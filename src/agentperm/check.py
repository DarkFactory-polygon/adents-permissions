"""Ядро check: точное посимвольное совпадение и срок; дата приходит аргументом (D-06)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from agentperm.record import Record


@dataclass(frozen=True)
class Decision:
    allowed: bool
    record: Record | None = None  # основание: действующая запись
    expired: bool = False  # отказ из-за срока, а не из-за отсутствия записи


def decide(
    records: list[Record], agent: str, action: str, resource: str, today: date
) -> Decision:
    matching = [
        r
        for r in records
        if r.agent == agent and r.action == action and r.resource == resource
    ]
    valid = [r for r in matching if r.until >= today]
    if valid:
        # наименьшая дата окончания, при равных — меньший порядковый номер (DEL-17)
        return Decision(True, min(valid, key=lambda r: (r.until, r.number)))
    return Decision(False, expired=bool(matching))
