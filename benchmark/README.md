# Бенчмарк: FastAPI vs Gin (Windows)

## Требования

- Windows 10 / 11 с PowerShell 5.1+
- Go-сервис запущен на порту **8080**
- Python-сервис запущен на порту **8000**
- Никаких сторонних утилит не нужно

## Структура файлов

```
benchmark/
├── run_benchmark.bat    ← запускать этот файл
├── benchmark_core.ps1   ← логика нагрузки (не трогать)
└── README.md
```

## Запуск

```bat
:: Терминал 1
cd go-service && go run .

:: Терминал 2
cd python-service && uvicorn main:app --port 8000

:: Терминал 3 — двойной клик или:
benchmark\run_benchmark.bat
```

> Если PowerShell выдаёт ошибку политики выполнения:
> ```bat
> powershell -ExecutionPolicy Bypass -File benchmark_core.ps1
> ```

## Параметры (в run_benchmark.bat)

| Переменная  | По умолчанию | Описание                        |
|-------------|-------------|---------------------------------|
| `REQUESTS`  | 200         | Кол-во запросов на каждый тест  |
| `THREADS`   | 4           | Параллельных потоков            |
| `GO_URL`    | localhost:8080 | Адрес Go-сервиса             |
| `PY_URL`    | localhost:8000 | Адрес Python-сервиса         |

## Что смотреть в выводе

| Метрика        | Что значит                  |
|----------------|-----------------------------|
| Requests/sec   | Пропускная способность      |
| Latency avg    | Среднее время ответа        |
| Latency max    | Худший случай               |

## Ожидаемый результат

`Invoke-WebRequest` добавляет накладные расходы PowerShell, поэтому абсолютные
цифры ниже, чем у `wrk`, но **соотношение** Go vs Python остаётся показательным.
Gin на `/ping` будет заметно быстрее FastAPI.
