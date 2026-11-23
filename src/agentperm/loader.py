"""Чтение файла прав: один документ YAML, композиция узлов (D-02, D-21, D-22)."""

from __future__ import annotations

import yaml

from agentperm.errors import RegistryError

TOP_KEY = "permissions"


def _line(node: yaml.Node) -> int:
    return node.start_mark.line + 1


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def load_records(path: str) -> list[yaml.MappingNode]:
    """Вернуть узлы записей списка `permissions`; любое отклонение — RegistryError."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except FileNotFoundError:
        raise RegistryError("файл прав не найден", path) from None
    except OSError as exc:
        reason = _one_line(exc.strerror or type(exc).__name__)
        raise RegistryError(f"файл прав не читается ({reason})", path) from None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise RegistryError("файл прав не является текстом UTF-8", path) from None

    try:
        documents = list(yaml.compose_all(text, Loader=yaml.SafeLoader))
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        problem = getattr(exc, "problem", None) or type(exc).__name__
        raise RegistryError(
            f"некорректный YAML ({_one_line(problem)})", path, line
        ) from None

    documents = [doc for doc in documents if doc is not None]
    if not documents:
        raise RegistryError("файл прав пуст", path)
    if len(documents) > 1:
        raise RegistryError(
            "в файле прав больше одного документа YAML", path, _line(documents[1])
        )

    root = documents[0]
    if not isinstance(root, yaml.MappingNode):
        raise RegistryError(
            f"верхний уровень должен быть отображением с ключом {TOP_KEY}",
            path,
            _line(root),
        )

    value: yaml.Node | None = None
    for key_node, val_node in root.value:
        key = key_node.value if isinstance(key_node, yaml.ScalarNode) else None
        if key != TOP_KEY:
            raise RegistryError(
                f"посторонний ключ верхнего уровня {key!r}", path, _line(key_node)
            )
        if value is not None:
            raise RegistryError(f"ключ {TOP_KEY} повторён", path, _line(key_node))
        value = val_node
    if value is None:
        raise RegistryError(f"нет ключа {TOP_KEY}", path, _line(root))
    if not isinstance(value, yaml.SequenceNode):
        raise RegistryError(f"значение {TOP_KEY} не список", path, _line(value))

    records: list[yaml.MappingNode] = []
    for number, item in enumerate(value.value, start=1):
        if not isinstance(item, yaml.MappingNode):
            raise RegistryError(
                "элемент списка не является отображением", path, _line(item), number
            )
        records.append(item)
    return records
