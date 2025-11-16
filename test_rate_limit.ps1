Write-Host "Testing rate limiting on login endpoint (max 5/minute)..." -ForegroundColor Cyan

for ($i=1; $i -le 7; $i++) {
    Write-Host "`nAttempt $i" ":" -NoNewline
    
    try {
        $body = @{username="test"; password="test"} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
        Write-Host " Success (unexpected)" -ForegroundColor Yellow
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        if ($statusCode -eq 429) {
            Write-Host " Status $statusCode - Rate limit working!" -ForegroundColor Green
        }
        elseif ($statusCode -eq 401) {
            Write-Host " Status $statusCode - Unauthorized (expected)" -ForegroundColor Gray
        }
        else {
            Write-Host " Status $statusCode" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host "`n`nDone!" -ForegroundColor Cyan

