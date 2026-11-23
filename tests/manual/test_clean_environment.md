# Ручная проверка: чистое окружение (BEH-30)

## MAN-NFR-09-python312-pyyaml-only

Покрывает: NFR-09, NFR-06. Сценарий: BEH-30. Поставка: DEL-35.
Контрольная дата: `2026-11-23` (дата прогона совпала с ней: `date +%F` → `2026-11-23`).

### 1. Установка в чистом окружении

Без компиляторов и системных пакетов: в окружение ставятся только готовые колёса (wheel).

```sh
uv venv --python 3.12 env
uv pip install --python env/bin/python pyyaml      # + pyyaml==6.0.4 (колесо, без сборки)
uv pip install --python env/bin/python --no-deps .  # + agentperm==0.1.0
env/bin/python -V                                    # Python 3.12.13
```

Ожидание: обе установки завершаются без ошибок, без сборки из исходников и без запроса
ключа, логина или лицензии.

### 2. Реестр R1 (`permissions.yaml` в текущем каталоге)

```yaml
permissions:
  - {agent: build-bot, resource: repo/app, action: read, granted_by: alice, until: 2026-12-31}
  - {agent: build-bot, resource: repo/app, action: write, granted_by: alice, until: 2026-11-23}
  - {agent: deploy-bot, resource: cluster/prod, action: deploy, granted_by: bob, until: 2026-11-22}
  - {agent: deploy-bot, resource: cluster/prod, action: deploy, granted_by: carol, until: 2026-12-05}
  - {agent: audit-bot, resource: repo/app, action: read, granted_by: bob, until: 2026-11-30}
  - {agent: lint-bot, resource: repo/app, action: read, granted_by: alice, until: 2026-12-01}
  - {agent: deploy-bot, resource: cluster/stage, action: deploy, granted_by: dave, until: 2026-11-25}
  - {agent: deploy-bot, resource: cluster/stage, action: deploy, granted_by: erin, until: 2026-11-20}
```

### 3. Прогоны сценариев (фактические выводы и коды выхода)

| Сценарий | Команда | Вывод | Код |
|---|---|---|---|
| BEH-01 | `python -m agentperm check build-bot read repo/app` | `разрешено: выдал alice, до 2026-12-31 (запись 1)` | 0 |
| BEH-02 | `python -m agentperm check build-bot write repo/app` | `разрешено: выдал alice, до 2026-11-23 (запись 2)` | 0 |
| BEH-03 | `python -m agentperm check deploy-bot deploy cluster/prod` | `разрешено: выдал carol, до 2026-12-05 (запись 4)` | 0 |

BEH-09, BEH-10, BEH-11: `python -m agentperm expired` на R1 (код 0):

```text
Просроченные:
  agent=deploy-bot resource=cluster/stage action=deploy granted_by=erin until=2026-11-20
  agent=deploy-bot resource=cluster/prod action=deploy granted_by=bob until=2026-11-22
Истекающие в ближайшие 7 дней:
  agent=build-bot resource=repo/app action=write granted_by=alice until=2026-11-23
  agent=deploy-bot resource=cluster/stage action=deploy granted_by=dave until=2026-11-25
  agent=audit-bot resource=repo/app action=read granted_by=bob until=2026-11-30
```

- BEH-09: в группах ровно записи 8, 3 и 2, 7, 5; записи 4, 6, 1 отсутствуют; строк записей пять.
- BEH-10: в каждой строке есть агент, ресурс, действие, «кто выдал», дата окончания.
- BEH-11: записи 7 и 8 (одно право `deploy-bot`/`deploy`/`cluster/stage`) — две отдельные строки в разных группах.

BEH-13: `expired` на файле из одной записи (`build-bot`, `until: 2026-12-31`):

```text
Просроченные:
Истекающие в ближайшие 7 дней:
```

Код выхода 0 — как на R1 (непустые группы), так и здесь (пустые группы); заголовки обеих групп есть.

### 4. Сторонние пакеты

`uv pip list --python env/bin/python`:

```text
Package   Version
--------- -------
agentperm 0.1.0
pyyaml    6.0.4
```

Кроме самого инструмента (`agentperm`) и PyYAML сторонних пакетов нет (список лишнего пуст).
Зависимость объявлена единственной: `pyyaml` в `[project].dependencies` файла `pyproject.toml`.

### 5. Регистрация, подписка, оплата

Шагов регистрации, входа, ввода ключа/лицензии, подписки и оплаты нет ни при установке,
ни при запуске; сервисов и сети инструмент не использует. Счёт за месяц работы — 0 рублей.

### Итог

Все ожидания выполнены → **зелёный** на BEH-30 (прогон 2026-11-23).
