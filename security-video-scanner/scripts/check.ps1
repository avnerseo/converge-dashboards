<#
.SYNOPSIS
    Checks that vscan is installed, finds your video files, and runs the
    footage report on the one you pick.

.DESCRIPTION
    This is the "what do I do now" script. Run it after setup.ps1:

        .\scripts\check.ps1

    It verifies the installation, lists the video files it can find on this
    machine with their full paths, and offers to run `vscan doctor` on one of
    them - so you never have to type a path by hand.

.PARAMETER Path
    Look for videos in this folder instead of the usual places
    (Videos, Desktop, Downloads, Documents). A network share works too:
    -Path "\\NAS\cctv"

.PARAMETER Deep
    Search every local drive instead. Slower - a minute or two - but it finds
    recordings sitting on D:, an external disk, or anywhere else.

.PARAMETER Samples
    How many frames the report samples. 60 is the default; 120 is slower but
    steadier on long recordings.
#>
[CmdletBinding()]
param(
    [string]$Path,
    [switch]$Deep,
    [int]$Samples = 60
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. (Join-Path $PSScriptRoot '_common.ps1')

# ------------------------------------------------------------ installation
Write-Head "Checking the installation"
$problems = 0

$ffmpeg = Resolve-FfmpegPath
if ($ffmpeg) {
    Write-Ok "ffmpeg ($ffmpeg)"
} else {
    Write-Bad "ffmpeg - run: powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1"
    $problems++
}

$vscan = Join-Path $root '.venv\Scripts\vscan.exe'
if (Test-Path $vscan) {
    Write-Ok "vscan ($(& $vscan --version))"
} else {
    Write-Bad "vscan - run: powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1"
    $problems++
}

if ($problems -eq 0) {
    $models = & $vscan models list 2>&1
    $missing = @($models | Where-Object { $_ -match 'not downloaded' })
    if ($missing.Count -gt 0) {
        Write-Bad "$($missing.Count) model(s) not downloaded - run: .\.venv\Scripts\vscan.exe models fetch"
        $problems++
    } else {
        Write-Ok "detection models"
    }
}

if ($problems -gt 0) {
    Write-Host "`nFix the items above, then run this script again." -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------------- find videos
Write-Head "Looking for video files"
$extensions = @('*.mp4', '*.mkv', '*.avi', '*.mov', '*.m4v', '*.mpg', '*.mpeg',
                '*.ts', '*.wmv', '*.asf', '*.dav', '*.webm')
$depth = 3
if ($Path) {
    $searchRoots = @($Path)
    $depth = 6
} elseif ($Deep) {
    $searchRoots = Get-PSDrive -PSProvider FileSystem |
                   Where-Object { $_.Free -ne $null } |
                   Select-Object -ExpandProperty Root
    $depth = 6
    Write-Host "  scanning every local drive - this can take a minute" -ForegroundColor DarkGray
} else {
    $searchRoots = @("$HOME\Videos", "$HOME\Desktop", "$HOME\Downloads",
                     "$HOME\Documents", "$HOME\OneDrive\Videos",
                     "$HOME\OneDrive\Desktop") |
                   Where-Object { Test-Path $_ }
}
if (-not $searchRoots) {
    Write-Host "  no folders to search - pass one, e.g.  .\scripts\check.ps1 -Path 'D:\cctv'" -ForegroundColor Yellow
    exit 1
}
foreach ($r in $searchRoots) { Write-Host "  searching $r" -ForegroundColor DarkGray }

$skip = '\\Windows\\|\\Program Files|\\AppData\\|\\\$Recycle|\\node_modules\\'
$files = @()
foreach ($r in $searchRoots) {
    $files += Get-ChildItem -LiteralPath $r -Include $extensions -File -Recurse -Depth $depth `
                            -ErrorAction SilentlyContinue |
              Where-Object { $_.FullName -notmatch $skip }
}
$files = $files | Sort-Object -Property FullName -Unique | Sort-Object -Property Length -Descending

if ($files.Count -eq 0) {
    Write-Host "`nNo video files found in those folders." -ForegroundColor Yellow
    Write-Host "Try one of these:" -ForegroundColor Yellow
    Write-Host "    .\scripts\check.ps1 -Deep                    # search every local drive"
    Write-Host "    .\scripts\check.ps1 -Path 'D:\cctv'          # a folder you know"
    Write-Host "    .\scripts\check.ps1 -Path '\\NAS\recordings'  # a network share"
    Write-Host "`nDrives on this machine:" -ForegroundColor Yellow
    Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -ne $null } |
        Format-Table Name, Root, @{n = 'Free GB'; e = { [math]::Round($_.Free / 1GB) } } -AutoSize
    exit 1
}

Write-Host ""
$shown = $files | Select-Object -First 25
for ($i = 0; $i -lt $shown.Count; $i++) {
    $size = '{0,8:N0} MB' -f ($shown[$i].Length / 1MB)
    Write-Host ("  [{0,2}] {1}  {2}" -f ($i + 1), $size, $shown[$i].Name)
    Write-Host ("       {0}" -f $shown[$i].FullName) -ForegroundColor DarkGray
}
if ($files.Count -gt $shown.Count) {
    Write-Host "  ... and $($files.Count - $shown.Count) more" -ForegroundColor DarkGray
}
if (-not $Path -and -not $Deep) {
    Write-Host "`n  Not the recordings you meant? Search wider:" -ForegroundColor DarkGray
    Write-Host "      .\scripts\check.ps1 -Deep                    # every local drive" -ForegroundColor DarkGray
    Write-Host "      .\scripts\check.ps1 -Path 'D:\cctv'          # a folder you know" -ForegroundColor DarkGray
    Write-Host "      .\scripts\check.ps1 -Path '\\NAS\recordings'  # a network share" -ForegroundColor DarkGray
}

# ------------------------------------------------------------------ report
Write-Host ""
$answer = Read-Host "Number of the video to check (Enter to skip)"
if ($answer -notmatch '^\s*\d+\s*$') {
    Write-Host "`nNothing checked. When you are ready:" -ForegroundColor White
    Write-Host "    .\.venv\Scripts\vscan.exe doctor `"<full path to a video>`""
    exit 0
}
$index = [int]$answer.Trim() - 1
if ($index -lt 0 -or $index -ge $shown.Count) {
    Write-Host "There is no number $($index + 1) in the list." -ForegroundColor Yellow
    exit 1
}

$chosen = $shown[$index].FullName
Write-Host "`nRunning the footage report on:`n    $chosen`n" -ForegroundColor Cyan
& $vscan doctor $chosen --samples $Samples

Write-Host @"

--------------------------------------------------------------------------
What to do with that report

  * "suggested command" above is the exact indexing command for this camera.
    Run it with the full vscan path, for example:

      .\.venv\Scripts\vscan.exe index "$chosen" --fps 2 --objects --appearance

  * then see who appears in it:

      .\.venv\Scripts\vscan.exe cluster --min-size 3 --report faces.html

  * or open the whole thing in a browser instead:

      .\scripts\start-server.ps1 -Footage "$(Split-Path -Parent $chosen)"

--------------------------------------------------------------------------
"@ -ForegroundColor White
