@echo off
setlocal enabledelayedexpansion

set GO_URL=http://localhost:8080
set PY_URL=http://localhost:8000
set REQUESTS=200
set THREADS=4

echo ========================================
echo Benchmark: Gin (Go) vs FastAPI (Python)
echo Requests: %REQUESTS% ^| Threads: %THREADS%
echo ========================================

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& { . '%~dp0benchmark_core.ps1'; Run-Benchmark -GoUrl '%GO_URL%' -PyUrl '%PY_URL%' -Requests %REQUESTS% -Threads %THREADS% }"

echo.
echo Done. Compare Requests/sec and Latency above.
pause
