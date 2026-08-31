<#
.SYNOPSIS
    Starts the vscan web interface on this machine.

.EXAMPLE
    .\scripts\start-server.ps1 -Footage "C:\videos"

.EXAMPLE
    .\scripts\start-server.ps1 -Footage "D:\cam-exports" -Password "my-strong-password" -Port 8090

.PARAMETER Footage
    The folder holding the recordings. It is only ever read, never written to.
    Several can be given, separated by commas. If it is left out, your Videos
    and Downloads folders are used - and you can always drag a file straight
    into the web page, whatever this is set to.

.PARAMETER Password
    Password for the 'admin' account. One is generated and printed if omitted.

.PARAMETER Port
    Defaults to 8080.

.PARAMETER Listen
    Also accept connections from other machines on the network. Off by
    default: without it the server answers only on this computer.
#>
[CmdletBinding()]
param(
    [string[]]$Footage,
    [string]$Password,
    [int]$Port = 8080,
    [switch]$Listen
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. (Join-Path $PSScriptRoot '_common.ps1')

if (-not (Resolve-FfmpegPath)) {
    Write-Host "ffmpeg is not installed - the server cannot read video without it." -ForegroundColor Yellow
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1"
    exit 1
}

$server = Join-Path $root '.venv\Scripts\vscan-server.exe'
if (-not (Test-Path $server)) {
    Write-Host "vscan is not installed yet. Run this first:" -ForegroundColor Yellow
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1"
    exit 1
}
# Somewhere to read from, without making the operator answer a question before
# they have seen the product. Footage can also be dragged into the web page.
if (-not $Footage) {
    $Footage = @("$HOME\Videos", "$HOME\Downloads") | Where-Object { Test-Path $_ }
    if ($Footage) {
        Write-Host "No -Footage given, so reading from your Videos and Downloads folders." -ForegroundColor DarkGray
    } else {
        Write-Host "No -Footage given and no Videos folder found - drag recordings into the web page." -ForegroundColor DarkGray
    }
}
$missing = $Footage | Where-Object { -not (Test-Path $_) }
if ($missing) {
    Write-Host "No such folder: $($missing -join ', ')" -ForegroundColor Yellow
    exit 1
}

# The admin account is created once, on the first run. Announcing a freshly
# generated password on later runs would be a lie: it is ignored, and the
# operator would be left trying a password that never existed.
$dataDir  = if ($env:VSCAN_DATA_DIR) { $env:VSCAN_DATA_DIR } else { Join-Path $root 'vscan-data' }
$firstRun = -not (Test-Path (Join-Path $dataDir 'app.db'))

if (-not $Password -and $firstRun) {
    $bytes = New-Object byte[] 12
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $Password = [Convert]::ToBase64String($bytes).TrimEnd('=')
    Write-Host "`nGenerated an admin password for this deployment:" -ForegroundColor Yellow
    Write-Host "    $Password" -ForegroundColor White
    Write-Host "Write it down - it is only shown now.`n" -ForegroundColor Yellow
} elseif (-not $firstRun) {
    if ($Password) {
        Write-Host "This machine already has an admin account, so -Password is ignored." -ForegroundColor DarkGray
        Write-Host "Forgotten it? Delete $dataDir and start again." -ForegroundColor DarkGray
        $Password = ''
    } else {
        Write-Host "Signing in with the admin account created on the first run." -ForegroundColor DarkGray
    }
}

$env:VSCAN_FOOTAGE_DIRS   = (($Footage | ForEach-Object { (Resolve-Path $_).Path }) -join ';')
$env:VSCAN_ADMIN_PASSWORD = $Password
$env:VSCAN_PORT           = "$Port"
# This machine only, unless asked otherwise - a face-recognition system should
# not be reachable from the rest of the network by accident.
$env:VSCAN_HOST = if ($Listen) { '0.0.0.0' } else { '127.0.0.1' }

Write-Host "footage : $(if ($env:VSCAN_FOOTAGE_DIRS) { $env:VSCAN_FOOTAGE_DIRS } else { 'uploads only' })"
Write-Host "sign in : http://localhost:$Port   (user: admin)" -ForegroundColor Green
if ($Listen) {
    Write-Host "reachable from the whole network - put it behind HTTPS before real use" -ForegroundColor Yellow
} else {
    Write-Host "this computer only (add -Listen to open it to the network)" -ForegroundColor DarkGray
}
Write-Host "Leave this window open. Ctrl+C stops the server.`n"

Start-Process "http://localhost:$Port"
& $server
