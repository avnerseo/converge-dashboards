<#
.SYNOPSIS
    Installs everything vscan needs on Windows: Python, ffmpeg, the package
    and the detection models.

.DESCRIPTION
    Run it from a PowerShell window, from inside the security-video-scanner
    folder:

        powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

    Safe to run more than once - it skips whatever is already in place.

.PARAMETER SkipTools
    Do not try to install Python or ffmpeg, just set up the virtual
    environment (use this if you installed them yourself).
#>
[CmdletBinding()]
param(
    [switch]$SkipTools
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. (Join-Path $PSScriptRoot '_common.ps1')

function Write-Step { param($n, $text) Write-Host "`n[$n] $text" -ForegroundColor Cyan }
function Have       { param($name) Test-Tool $name }

function Get-PythonCommand {
    foreach ($candidate in @('py', 'python3', 'python')) {
        if (-not (Have $candidate)) { continue }
        try { $version = & $candidate --version 2>&1 } catch { continue }
        if ($version -match 'Python (\d+)\.(\d+)') {
            $major = [int]$Matches[1]; $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 10) { return $candidate }
        }
    }
    return $null
}

Write-Host "vscan setup" -ForegroundColor White
Write-Host "working in $root"

# ---------------------------------------------------------------- 1. Python
Write-Step 1 "Python 3.10 or newer"
$python = Get-PythonCommand
if (-not $python -and -not $SkipTools) {
    if (-not (Have 'winget')) {
        Write-Warn "winget is not available. Install Python 3.12 from python.org,"
        Write-Warn "tick 'Add python.exe to PATH', then run this script again."
        exit 1
    }
    Write-Host "    installing Python 3.12 with winget..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    Update-PathFromRegistry
    $python = Get-PythonCommand
}
if (-not $python) {
    Write-Warn "Python is installed but this window cannot see it yet."
    Write-Warn "Close PowerShell, open it again, and run this script once more."
    exit 1
}
Write-Ok "$python -> $(& $python --version)"

# ---------------------------------------------------------------- 2. ffmpeg
Write-Step 2 "ffmpeg (this is what opens the video files)"
$ffmpeg = Resolve-FfmpegPath
if (-not $ffmpeg -and -not $SkipTools) {
    if (-not (Have 'winget')) {
        Write-Warn "winget is not available. Install ffmpeg manually and re-run."
        exit 1
    }
    Write-Host "    installing ffmpeg with winget..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    $ffmpeg = Resolve-FfmpegPath
}
if (-not $ffmpeg) {
    Write-Warn "ffmpeg is installed but cannot be found on this machine."
    Write-Warn "Close PowerShell, open it again, and run this script once more."
    exit 1
}
Write-Ok "ffmpeg ($ffmpeg)"

# ------------------------------------------------------- 3. virtualenv + app
Write-Step 3 "Python environment and vscan itself"
$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    & $python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Warn "could not create the .venv folder"; exit 1 }
}
& $venvPython -m pip install --quiet --upgrade pip
& $venvPython -m pip install --quiet -e ".[server,ask]"
if ($LASTEXITCODE -ne 0) { Write-Warn "installing vscan failed - see the output above"; exit 1 }
Write-Ok "vscan installed into .venv"

# ---------------------------------------------------------------- 4. models
Write-Step 4 "Detection models (about 140 MB, downloaded once)"
$vscan = Join-Path $root '.venv\Scripts\vscan.exe'
& $vscan models fetch
if ($LASTEXITCODE -ne 0) {
    Write-Warn "the models could not be downloaded - check the internet connection"
    exit 1
}
Write-Ok "models ready"

# ------------------------------------------------------------------ 5. done
Write-Host "`nReady." -ForegroundColor Green
Write-Host @"

Next, check one of your videos before indexing anything:

    .\.venv\Scripts\vscan.exe doctor "C:\path\to\your\video.mp4"

It samples the file and tells you whether faces are big enough to identify,
whether appearance search will work, and exactly which index command to run.

To open the full web interface instead:

    .\scripts\start-server.ps1 -Footage "C:\path\to\your\videos"

"@ -ForegroundColor White
