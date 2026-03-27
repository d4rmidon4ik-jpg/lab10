# Бенчмарк: FastAPI vs Gin

## Требования

- Apache Bench (`ab.exe`) — входит в состав [Apache HTTP Server](https://www.apachelounge.com/download/)
- Go-сервис запущен на порту 8080
- Python-сервис запущен на порту 8000

## Настройка пути к ab.exe

В `run_benchmark.sh` укажи свой путь к `ab.exe`:
```bash
AB_PATH="/c/Users/user/Desktop/Apache24/bin/ab.exe"
```

## Запуск
```bash
# Терминал 1
cd go-service && go run .

# Терминал 2
cd python-service && uvicorn main:app --port 8000

# Терминал 3
chmod +x benchmark/run_benchmark.sh
./benchmark/run_benchmark.sh
```

## Параметры теста

| Параметр | Значение |
|---|---|
| Инструмент | Apache Bench (ab) |
| Длительность | 10 секунд на тест |
| Параллельных соединений | 50 |

## Тестируемые эндпоинты

| Тест | Метод | URL |
|---|---|---|
| Go Gin ping | GET | `http://localhost:8080/ping` |
| FastAPI ping | GET | `http://localhost:8000/go/ping` |
| Go Gin calculate | POST | `http://localhost:8080/calculate` |
| FastAPI calculate | POST | `http://localhost:8000/go/calculate` |

## Что смотреть в выводе

| Метрика | Что значит |
|---|---|
| Requests per second | Пропускная способность — чем выше, тем лучше |
| Time per request (mean) | Среднее время ответа — чем ниже, тем лучше |
| Failed requests | Должно быть 0 |
| Complete requests | Общее число выполненных запросов за 10с |

## Ожидаемый результат

Gin (Go) даёт значительно больше Requests/sec на `/ping` — компилируемый язык без overhead.  
FastAPI на `/go/calculate` медленнее вдвойне: Python-overhead + дополнительный HTTP-вызов к Go-сервису.