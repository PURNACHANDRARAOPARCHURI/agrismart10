<#
Dev setup script for local development (Windows PowerShell)

Usage: open a PowerShell terminal in the `backend` folder and run:
    ./dev-setup.ps1

This script will:
- create a virtualenv `.venv` if missing
- upgrade pip/setuptools/wheel
- install minimal packages for quick local dev
- set DB_ENGINE=sqlite for this session
- run migrations, seed crops, and start the Django dev server
- write a transcript log to `dev-setup-log.txt`

Important: the script runs `manage.py runserver` in foreground. Press CTRL+C to stop.
#>

Set-StrictMode -Version Latest

Write-Host "Running dev-setup.ps1 in: $(Get-Location)"

# 1) Create .venv if missing
if (-not (Test-Path -LiteralPath '.venv')) {
    Write-Host "Creating virtualenv .venv..."
    py -3 -m venv .venv
} else {
    Write-Host ".venv already exists - will reuse it"
}

# 2) Prepare log transcript
$log = Join-Path -Path (Get-Location) -ChildPath 'dev-setup-log.txt'
if (Test-Path $log) { Remove-Item $log -Force }
Start-Transcript -Path $log -Force

try {
    # 3) Upgrade packaging tools
    Write-Host "=== Upgrading pip, setuptools and wheel ==="
    .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

    # 4) Install minimal packages for quick local dev
    Write-Host "=== Installing minimal packages for local dev ==="
    .\.venv\Scripts\python.exe -m pip install Django djangorestframework dj-database-url django-cors-headers --default-timeout=60 --retries=5

    Write-Host "=== Confirming dj-database-url is installed ==="
    $pkg = .\.venv\Scripts\python.exe -m pip show dj-database-url 2>$null
    if (-not $pkg) {
        Write-Host "dj-database-url not found"
    } else {
        Write-Host $pkg
    }

    # 5) Use sqlite for this session to avoid installing mysqlclient on Windows
    Write-Host "=== Setting DB_ENGINE=sqlite for this session ==="
    $env:DB_ENGINE = 'sqlite'

    # 6) Run migrations and seed data
    Write-Host "=== Running migrations ==="
    .\.venv\Scripts\python.exe manage.py migrate --noinput

    Write-Host "=== Seeding crops ==="
    .\.venv\Scripts\python.exe manage.py seed_crops

    # 7) Start development server (foreground)
    Write-Host "=== Starting Django dev server on http://127.0.0.1:8000 ==="
    .\.venv\Scripts\python.exe manage.py runserver

} catch {
    Write-Error "An error occurred: $_"
    throw
} finally {
    # The transcript will continue until the session ends or Stop-Transcript is called.
    Write-Host "If the server stopped, run Stop-Transcript to close the log file. Log path: $log"
}

# End of script