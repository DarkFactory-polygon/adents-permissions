"""Точка входа: разбор argv, две команды, единая обработка ошибок (D-11..D-14)."""

from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from agentperm import clock, render
from agentperm.check import decide, split_expiry
from agentperm.errors import RegistryError
from agentperm.loader import load_records

DEFAULT_FILE = "permissions.yaml"


USAGE = (
    "использование: agentperm check АГЕНТ ДЕЙСТВИЕ РЕСУРС [--file ПУТЬ]\n"
    "               agentperm expired [--file ПУТЬ]"
)


class _Parser(argparse.ArgumentParser):
    """Ошибка вызова: одна строка + подсказка с двумя командами, код 2 (D-13)."""

    def error(self, message: str) -> NoReturn:
        print(f"ошибка: неверный вызов\n{USAGE}", file=sys.stderr)
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="agentperm", usage=USAGE)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    check = sub.add_parser("check", help="проверить право агента")
    check.add_argument("agent")
    check.add_argument("action")
    check.add_argument("resource")
    check.add_argument("--file", default=DEFAULT_FILE)
    expired = sub.add_parser("expired", help="показать просроченные и истекающие права")
    expired.add_argument("--file", default=DEFAULT_FILE)
    return parser


def _run(args: argparse.Namespace) -> int:
    records = load_records(args.file)  # любая ошибка файла — до какого-либо ответа
    if args.command == "check":
        decision = decide(records, args.agent, args.action, args.resource, clock.today())
        print(render.decision_line(decision))
        return 0 if decision.allowed else 1
    overdue, expiring = split_expiry(records, clock.today())
    print(render.HEADER_EXPIRED)
    for rec in overdue:
        print(render.record_row(rec))
    print(render.HEADER_EXPIRING)
    for rec in expiring:
        print(render.record_row(rec))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except RegistryError as exc:
        print(exc.render(), file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 — трассировка не печатается никогда (D-12)
        error = RegistryError(f"внутренняя ошибка ({type(exc).__name__})", args.file)
        print(error.render(), file=sys.stderr)
    return 2


def entrypoint() -> None:
    sys.exit(main())
