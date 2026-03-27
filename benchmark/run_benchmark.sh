#!/usr/bin/env bash
set -e

GO_URL="http://localhost:8080"
PY_URL="http://localhost:8000"
CONCURRENCY=50
DURATION=10  # секунд
AB_PATH="/c/Users/user/Desktop/Apache24/bin/ab.exe"
RESULTS_FILE="results.txt"

echo "========================================"
echo "Benchmark: Gin (Go) vs FastAPI (Python)"
echo "Duration: ${DURATION}s | Concurrency: ${CONCURRENCY}"
echo "========================================"

if [ ! -f "$AB_PATH" ]; then
    echo "ERROR: ab not found at $AB_PATH"
    exit 1
fi

{
    echo "========================================"
    echo "Benchmark: Gin (Go) vs FastAPI (Python)"
    echo "Date: $(date)"
    echo "Duration: ${DURATION}s | Concurrency: ${CONCURRENCY}"
    echo "========================================"
} > "$RESULTS_FILE"

run_ab_test() {
    local url=$1
    local name=$2
    local method=${3:-GET}
    local data=${4:-""}

    echo ""
    echo "--- $name ---"
    echo "URL: $url"

    # Захватываем вывод ab в переменную
    local output=""
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        temp_file=$(mktemp)
        echo "$data" > "$temp_file"

        echo "Running test for ${DURATION} seconds with ${CONCURRENCY} concurrent connections..."
        output=$("$AB_PATH" -t $DURATION \
                             -c $CONCURRENCY \
                             -T "application/json" \
                             -p "$temp_file" \
                             "$url" 2>&1 | grep -E "(Requests per second|Time per request|Transfer rate|Complete requests|Failed requests)")
        rm "$temp_file"
    else
        echo "Running test for ${DURATION} seconds with ${CONCURRENCY} concurrent connections..."
        output=$("$AB_PATH" -t $DURATION \
                             -c $CONCURRENCY \
                             "$url" 2>&1 | grep -E "(Requests per second|Time per request|Transfer rate|Complete requests|Failed requests)")
    fi

    # Выводим в терминал
    echo "$output"

    # Пишем в файл
    {
        echo ""
        echo "--- $name ---"
        echo "URL: $url"
        echo "$output"
    } >> "$RESULTS_FILE"
}

run_ab_test "${GO_URL}/ping"        "Go Gin: GET /ping"            "GET"
run_ab_test "${PY_URL}/go/ping"     "FastAPI: GET /go/ping"        "GET"

POST_DATA='{"a":10,"b":3,"op":"add"}'
run_ab_test "${GO_URL}/calculate"     "Go Gin: POST /calculate"        "POST" "$POST_DATA"
run_ab_test "${PY_URL}/go/calculate"  "FastAPI: POST /go/calculate"    "POST" "$POST_DATA"

{
    echo ""
    echo "========================================"
    echo "Benchmark completed!"
    echo "Key metric: Requests per second (higher is better)"
    echo "Time per request (mean): lower is better"
    echo "========================================"
} | tee -a "$RESULTS_FILE"

echo ""
echo "Results saved to: $RESULTS_FILE"