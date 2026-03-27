function Invoke-LoadTest {
    param(
        [string]$Label,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [int]$Requests,
        [int]$Threads
    )

    Write-Host ""
    Write-Host "--- $Label ---" -ForegroundColor Cyan

    $perThread = [math]::Ceiling($Requests / $Threads)
    $jobs = @()

    $sw = [System.Diagnostics.Stopwatch]::StartNew()

    for ($i = 0; $i -lt $Threads; $i++) {
        $jobs += Start-Job -ScriptBlock {
            param($url, $method, $body, $count)

            $ok = 0; $fail = 0; $latencies = @()

            for ($j = 0; $j -lt $count; $j++) {
                $t = [System.Diagnostics.Stopwatch]::StartNew()
                try {
                    if ($method -eq "POST") {
                        $null = Invoke-WebRequest -Uri $url -Method POST `
                            -ContentType "application/json" -Body $body -UseBasicParsing -TimeoutSec 10
                    } else {
                        $null = Invoke-WebRequest -Uri $url -Method GET `
                            -UseBasicParsing -TimeoutSec 10
                    }
                    $ok++
                } catch {
                    $fail++
                }
                $t.Stop()
                $latencies += $t.Elapsed.TotalMilliseconds
            }

            return @{ Ok=$ok; Fail=$fail; Latencies=$latencies }
        } -ArgumentList $Url, $Method, $Body, $perThread
    }

    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job

    $sw.Stop()

    $totalOk   = 0
    $totalFail = 0
    $allLat    = @()

    foreach ($r in $results) {
        $totalOk   += $r.Ok
        $totalFail += $r.Fail
        $allLat    += $r.Latencies
    }

    $elapsed = $sw.Elapsed.TotalSeconds
    $rps     = [math]::Round($totalOk / $elapsed, 2)
    $avgLat  = [math]::Round(($allLat | Measure-Object -Average).Average, 2)
    $maxLat  = [math]::Round(($allLat | Measure-Object -Maximum).Maximum, 2)
    $minLat  = [math]::Round(($allLat | Measure-Object -Minimum).Minimum, 2)

    Write-Host ("  Requests sent : {0} ok, {1} failed" -f $totalOk, $totalFail)
    Write-Host ("  Duration      : {0:F2} s" -f $elapsed)
    Write-Host ("  Requests/sec  : {0}" -f $rps)        -ForegroundColor Green
    Write-Host ("  Latency avg   : {0} ms" -f $avgLat)
    Write-Host ("  Latency min   : {0} ms" -f $minLat)
    Write-Host ("  Latency max   : {0} ms" -f $maxLat)  -ForegroundColor Yellow

    return $rps
}

function Run-Benchmark {
    param(
        [string]$GoUrl,
        [string]$PyUrl,
        [int]$Requests,
        [int]$Threads
    )

    $calcBody = '{"a":10,"b":3,"op":"add"}'

    $goGet  = Invoke-LoadTest -Label "Go Gin:  GET  /ping"        -Url "$GoUrl/ping"         -Method GET  -Requests $Requests -Threads $Threads
    $pyGet  = Invoke-LoadTest -Label "FastAPI: GET  /go/ping"     -Url "$PyUrl/go/ping"       -Method GET  -Requests $Requests -Threads $Threads
    $goPost = Invoke-LoadTest -Label "Go Gin:  POST /calculate"   -Url "$GoUrl/calculate"     -Method POST -Body $calcBody -Requests $Requests -Threads $Threads
    $pyPost = Invoke-LoadTest -Label "FastAPI: POST /go/calculate" -Url "$PyUrl/go/calculate" -Method POST -Body $calcBody -Requests $Requests -Threads $Threads

    Write-Host ""
    Write-Host "========== SUMMARY (Requests/sec) ==========" -ForegroundColor Magenta
    Write-Host ("  GET  /ping       -- Go: {0,8}   Python: {1,8}" -f $goGet,  $pyGet)
    Write-Host ("  POST /calculate  -- Go: {0,8}   Python: {1,8}" -f $goPost, $pyPost)

    if ($pyGet -gt 0) {
        $ratio = [math]::Round($goGet / $pyGet, 2)
        Write-Host ("  Go быстрее в {0}x на GET /ping" -f $ratio) -ForegroundColor Green
    }
    Write-Host "=============================================" -ForegroundColor Magenta
}
