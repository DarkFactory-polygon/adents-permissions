"""Единая форма ошибки (D-12): что случилось + где."""

from __future__ import annotations


class RegistryError(Exception):
    """Негодное состояние реестра; печатается одной строкой, код выхода 2."""

    def __init__(
        self,
        what: str,
        path: str,
        line: int | None = None,
        record: int | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(what)
        self.what = what
        self.path = path
        self.line = line
        self.record = record
        self.field = field

    def render(self) -> str:
        where: list[str] = []
        if self.line is not None:
            where.append(f"строка {self.line}")
        if self.record is not None:
            where.append(f"запись {self.record}")
        if self.field is not None:
            where.append(f"поле {self.field}")
        text = f"ошибка: {self.what}: {self.path}"
        if where:
            text += f": {', '.join(where)}"
        return " ".join(text.split("\n"))
