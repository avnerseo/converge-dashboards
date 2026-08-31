<#
    Shared helpers for the vscan PowerShell scripts. Dot-sourced, not run:

        . (Join-Path $PSScriptRoot '_common.ps1')
#>

function Write-Ok   { param($t) Write-Host "  OK   $t" -ForegroundColor Green }
function Write-Bad  { param($t) Write-Host "  MISS $t" -ForegroundColor Red }
function Write-Warn { param($t) Write-Host "    !   $t" -ForegroundColor Yellow }
function Write-Head { param($t) Write-Host "`n$t" -ForegroundColor Cyan }
function Test-Tool  { param($name) [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Update-PathFromRegistry {
    <#  winget writes the new PATH to the registry, but a window that was
        already open keeps the PATH it started with. Re-read it so the tool
        just installed is usable without closing anything.  #>
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user    = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
}

function Resolve-FfmpegPath {
    <#  Returns the path to ffmpeg.exe, adding its folder to this session's
        PATH when it is installed but not visible yet. Returns $null when
        ffmpeg really is not installed.  #>
    if (Test-Tool 'ffmpeg') { return (Get-Command ffmpeg).Source }

    Update-PathFromRegistry
    if (Test-Tool 'ffmpeg') { return (Get-Command ffmpeg).Source }

    # winget installs a shim under WinGet\Links - check that before scanning
    $direct = @(
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\ffmpeg.exe'),
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\ffmpeg.exe')
    )
    foreach ($candidate in $direct) {
        if ($candidate -and (Test-Path $candidate)) {
            $env:Path = "$(Split-Path -Parent $candidate);$env:Path"
            return $candidate
        }
    }

    # last resort: look inside the usual install roots (a few seconds)
    foreach ($base in @((Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'),
                        $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if (-not $base -or -not (Test-Path $base)) { continue }
        $found = Get-ChildItem -Path $base -Filter 'ffmpeg.exe' -Recurse -File `
                               -Depth 4 -ErrorAction SilentlyContinue |
                 Select-Object -First 1 -ExpandProperty FullName
        if ($found) {
            $env:Path = "$(Split-Path -Parent $found);$env:Path"
            return $found
        }
    }
    return $null
}
