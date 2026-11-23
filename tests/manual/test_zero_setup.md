# Ручная проверка: пустой каталог без сервера, базы данных и настройки (BEH-31)

## MAN-NFR-10-empty-dir-no-server-no-db

Покрывает: NFR-10. Сценарий: BEH-31. Поставка: DEL-36.
Контрольная дата: `2026-11-23` (`date +%F` → `2026-11-23`).

### 1. Подготовка

Окружение — как в BEH-30 (Python 3.12.13 и только PyYAML, `agentperm` установлен):

```sh
uv venv --python 3.12 env
uv pip install --python env/bin/python pyyaml
uv pip install --python env/bin/python --no-deps .
mkdir work && cd work        # пустой каталог
```

В каталог кладётся единственный файл `permissions.yaml` — реестр R1 из
`test_clean_environment.md` (8 записей). Больше ничего: нет файла настройки,
базы данных, переменных окружения, запущенного сервера.

```sh
ls -A     # → permissions.yaml
```

Перед прогоном снят список процессов (`ps -eo pid,comm`).

### 2. Прогон сразу после установки

| Команда | Вывод | Код |
|---|---|---|
| `python -m agentperm check build-bot read repo/app` | `разрешено: выдал alice, до 2026-12-31 (запись 1)` | 0 |
| `python -m agentperm check build-bot write repo/app` | `разрешено: выдал alice, до 2026-11-23 (запись 2)` | 0 |
| `python -m agentperm check deploy-bot deploy cluster/prod` | `разрешено: выдал carol, до 2026-12-05 (запись 4)` | 0 |

`python -m agentperm expired` (код 0):

```text
Просроченные:
  agent=deploy-bot resource=cluster/stage action=deploy granted_by=erin until=2026-11-20
  agent=deploy-bot resource=cluster/prod action=deploy granted_by=bob until=2026-11-22
Истекающие в ближайшие 7 дней:
  agent=build-bot resource=repo/app action=write granted_by=alice until=2026-11-23
  agent=deploy-bot resource=cluster/stage action=deploy granted_by=dave until=2026-11-25
  agent=audit-bot resource=repo/app action=read granted_by=bob until=2026-11-30
```

Выводы и коды выхода совпали с ожидаемыми; ни одной подготовительной команды
(`init`, `setup`, миграции, запуск сервиса) не потребовалось.

### 3. Состояние после завершения

- `ls -A` в каталоге после прогонов: по-прежнему только `permissions.yaml` — ни базы
  данных, ни файла настройки, ни lock/кэша не создано.
- Сравнение `ps -eo pid,comm` до и после: новых процессов (python, agentperm) нет;
  каждая команда — одиночный процесс, завершившийся сам.
- Новых слушающих портов инструмент не открывал (единственный python с портами в системе
  — посторонний, был в списке процессов до прогона); служб и демонов не устанавливалось.

### Итог

Все ожидания выполнены → **зелёный** на BEH-31 (прогон 2026-11-23).
