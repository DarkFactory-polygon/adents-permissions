"""Фиксированный текст ответов (D-20)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentperm.check import Decision
    from agentperm.record import Record

DENY_NO_RECORD = "запрещено: записи нет"
DENY_EXPIRED = "запрещено: срок истёк"
HEADER_EXPIRED = "Просроченные:"
HEADER_EXPIRING = "Истекающие в ближайшие 7 дней:"


def decision_line(decision: Decision) -> str:
    if decision.allowed and decision.record is not None:
        rec = decision.record
        return (
            f"разрешено: выдал {rec.granted_by}, до {rec.until.isoformat()}"
            f" (запись {rec.number})"
        )
    return DENY_EXPIRED if decision.expired else DENY_NO_RECORD


def record_row(rec: Record) -> str:
    """Строка группы expired: все пять полей, значения как в файле."""
    return (
        f"  agent={rec.agent} resource={rec.resource} action={rec.action}"
        f" granted_by={rec.granted_by} until={rec.until.isoformat()}"
    )
