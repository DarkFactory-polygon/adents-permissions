"""Единственное чтение локальной даты (D-06)."""

from datetime import date


def today() -> date:
    return date.today()
