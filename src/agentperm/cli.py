"""Точка входа: разбор argv, две команды, единая обработка ошибок (D-11..D-14)."""

from __future__ import annotations

import argparse
import sys

from agentperm import render
from agentperm.errors import RegistryError
from agentperm.loader import load_records

DEFAULT_FILE = "permissions.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentperm")
    sub = parser.add_subparsers(dest="command", required=True)
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
        # Сопоставление записей — TASK-003; до него отказ по умолчанию (NFR-01).
        _ = records
        print(render.DENY_NO_RECORD)
        return 1
    # Разбиение на группы — TASK-004.
    print(render.HEADER_EXPIRED)
    print(render.HEADER_EXPIRING)
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
