# Python Gateway Service — Integration Tests

Интеграционные тесты проверяют работу FastAPI-прокси совместно с реальным Go-сервисом.

---

## Требования

- Python 3.11+
- Go-сервис запущен на `http://localhost:8080`

---

## Установка зависимостей

```bash
pip install fastapi httpx pytest anyio pytest-asyncio uvicorn
```

---

## Запуск Go-сервиса

Перед запуском тестов Go-сервис должен быть поднят. Из директории Go-сервиса:

```bash
go run main.go
```

Убедитесь, что сервис отвечает:

```bash
curl http://localhost:8080/ping
# {"message":"pong","status":"ok"}
```

---

## Запуск тестов

Из директории `python-service`:

```bash
pytest test_main.py -v
```

### Ожидаемый результат

```
test_main.py::test_health_status                        PASSED
test_main.py::test_proxy_ping_ok                        PASSED
test_main.py::test_proxy_calculate_add                  PASSED
test_main.py::test_proxy_calculate_sub                  PASSED
test_main.py::test_proxy_calculate_mul                  PASSED
test_main.py::test_proxy_calculate_div                  PASSED
test_main.py::test_proxy_calculate_division_by_zero     PASSED
test_main.py::test_proxy_calculate_invalid_op           PASSED
test_main.py::test_proxy_calculate_missing_fields       PASSED
test_main.py::test_proxy_calculate_negative_numbers     PASSED
test_main.py::test_proxy_item_valid                     PASSED
test_main.py::test_proxy_item_not_found                 PASSED
test_main.py::test_proxy_item_zero                      PASSED
test_main.py::test_calculate_request_model_rejects_invalid_op PASSED
```

---

## Что тестируется

| Тест | Описание |
|---|---|
| `test_health_status` | Healthcheck самого Python-сервиса |
| `test_proxy_ping_ok` | Проксирование `/ping` к Go |
| `test_proxy_calculate_*` | Арифметические операции через Go |
| `test_proxy_calculate_division_by_zero` | Go возвращает 422 при делении на ноль |
| `test_proxy_calculate_invalid_op` | Pydantic отклоняет недопустимую операцию до Go |
| `test_proxy_calculate_missing_fields` | Pydantic отклоняет неполный запрос |
| `test_proxy_item_valid` | Получение существующего item по id |
| `test_proxy_item_not_found` / `_zero` | Go возвращает 404 для id ≤ 0 |
| `test_calculate_request_model_rejects_invalid_op` | Unit-тест Pydantic-модели |

---

## Если тесты падают

**`RuntimeError: HTTP client is not initialized`**
Убедитесь, что используете актуальную версию `test_main.py` — `TestClient` должен запускаться через контекстный менеджер (`with TestClient(app)`), иначе `lifespan` не выполняется.

**`httpx.ConnectError` / `502`**
Go-сервис не запущен или слушает другой порт. Проверьте `http://localhost:8080/ping`.
