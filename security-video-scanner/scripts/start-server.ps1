<#
.SYNOPSIS
    Starts the vscan web interface on this machine.

.EXAMPLE
    .\scripts\start-server.ps1 -Footage "C:\videos"

.EXAMPLE
    .\scripts\start-server.ps1 -Footage "D:\cam-exports" -Password "my-strong-password" -Port 8090

.PARAMETER Footage
    The folder holding the recordings. It is only ever read, never written to.

.PARAMETER Password
    Password for the 'admin' account. One is generated and printed if omitted.

.PARAMETER Port
    Defaults to 8080.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Footage,
    [string]$Password,
    [int]$Port = 8080
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
if (-not (Test-Path $Footage)) {
    Write-Host "No such folder: $Footage" -ForegroundColor Yellow
    exit 1
}

if (-not $Password) {
    $bytes = New-Object byte[] 12
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $Password = [Convert]::ToBase64String($bytes).TrimEnd('=')
    Write-Host "`nGenerated an admin password for this deployment:" -ForegroundColor Yellow
    Write-Host "    $Password" -ForegroundColor White
    Write-Host "Write it down - it is only shown now.`n" -ForegroundColor Yellow
}

$env:VSCAN_FOOTAGE_DIRS  = (Resolve-Path $Footage).Path
$env:VSCAN_ADMIN_PASSWORD = $Password
$env:VSCAN_PORT           = "$Port"

Write-Host "footage : $env:VSCAN_FOOTAGE_DIRS"
Write-Host "sign in : http://localhost:$Port   (user: admin)" -ForegroundColor Green
Write-Host "Leave this window open. Ctrl+C stops the server.`n"

Start-Process "http://localhost:$Port"
& $server
