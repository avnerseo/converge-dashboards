# Free Claude Code (FCC) - isolated launcher for Windows PowerShell.
#
# Runs the FCC proxy (https://github.com/Alishahryar1/free-claude-code) and points
# a SEPARATE Claude Code profile at it. Your existing Claude Code install, login and
# settings are never touched: everything lives under $FccHome and the proxied
# Claude Code runs with its own CLAUDE_CONFIG_DIR.
#
# Three ways to run Claude Code, from one place:
#   .\fcc.ps1 claude  - through the local proxy (free third-party models)
#   .\fcc.ps1 api     - straight to Anthropic with your own API key (billed per
#                       token, does NOT consume your subscription quota)
#   plain `claude`    - your normal subscription install, untouched by this script
#
# Usage:  .\fcc.ps1 setup | start | claude | api | status | stop | uninstall
# If PowerShell blocks the script:  Set-ExecutionPolicy -Scope Process Bypass

param(
    [Parameter(Position = 0)]
    [ValidateSet('setup', 'start', 'claude', 'api', 'status', 'stop', 'uninstall')]
    [string]$Command = 'status',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'

$FccHome  = if ($env:FCC_HOME) { $env:FCC_HOME } else { Join-Path $HOME '.free-claude-code' }
$FccPort  = if ($env:FCC_PORT) { [int]$env:FCC_PORT } else { 8082 }
$AppDir    = Join-Path $FccHome 'app'
$EnvFile   = Join-Path $AppDir  '.env'
$ConfigDir    = Join-Path $FccHome 'claude-config'
$ApiConfigDir = Join-Path $FccHome 'api-config'
$KeyFile      = Join-Path $FccHome 'api-key'
$LogFile   = Join-Path $FccHome 'server.log'
$PidFile   = Join-Path $FccHome 'server.pid'
$RepoUrl   = 'https://github.com/Alishahryar1/free-claude-code.git'

function Write-Info { param($m) Write-Host "==> $m" -ForegroundColor Cyan }
function Write-Warn { param($m) Write-Host "warn: $m" -ForegroundColor Yellow }
function Die       { param($m) Write-Host "error: $m" -ForegroundColor Red; exit 1 }
function Have      { param($c) [bool](Get-Command $c -ErrorAction SilentlyContinue) }

function Test-PortOpen {
    try {
        $c = [System.Net.Sockets.TcpClient]::new()
        $ok = $c.ConnectAsync('127.0.0.1', $FccPort).Wait(700)
        $c.Close()
        return $ok
    } catch { return $false }
}

function Invoke-Setup {
    if (-not (Have git))  { Die 'git is required (https://git-scm.com/download/win)' }
    if (-not (Have uv))   { Die 'uv is not installed. Install it first (see README, step 1) and re-run.' }
    if (-not (Have claude)) { Write-Warn "the 'claude' command was not found - install Claude Code before using '.\fcc.ps1 claude'" }

    New-Item -ItemType Directory -Force -Path $FccHome, $ConfigDir | Out-Null

    if (Test-Path (Join-Path $AppDir '.git')) {
        Write-Info "updating existing checkout in $AppDir"
        git -C $AppDir pull --ff-only
    } else {
        Write-Info "cloning FCC into $AppDir"
        git clone --depth 1 $RepoUrl $AppDir
    }

    Write-Info 'resolving python dependencies (uv sync)'
    Push-Location $AppDir; try { uv sync } finally { Pop-Location }

    if (Test-Path $EnvFile) {
        Write-Info ".env already exists - leaving it as is (edit $EnvFile to change provider)"
    } else {
        $example = Join-Path $AppDir '.env.example'
        if (Test-Path $example) { Copy-Item $example $EnvFile } else { New-Item -ItemType File -Path $EnvFile | Out-Null }

        Write-Host ''
        Write-Host 'Which provider should the proxy use?'
        Write-Host '  1) OpenRouter   (recommended: you can opt out of training in account settings)'
        Write-Host '  2) NVIDIA NIM   (bigger free quota, but free-tier inputs are used for training)'
        Write-Host '  3) Local only   (LM Studio / Ollama - nothing leaves your machine)'
        $choice = Read-Host 'choice [1]'
        $keyVar = switch ($choice) { '2' { 'NVIDIA_NIM_API_KEY' } '3' { '' } default { 'OPENROUTER_API_KEY' } }

        if ($keyVar) {
            $secure = Read-Host "$keyVar (input hidden)" -AsSecureString
            $plain  = [System.Net.NetworkCredential]::new('', $secure).Password
            if (-not $plain) { Die 'no key entered' }
            $lines = @()
            if (Test-Path $EnvFile) { $lines = Get-Content $EnvFile | Where-Object { $_ -notmatch "^$keyVar=" } }
            $lines += "$keyVar=$plain"
            Set-Content -Path $EnvFile -Value $lines -Encoding utf8
            Write-Info "wrote $keyVar to $EnvFile"
        } else {
            Write-Info 'no cloud key stored - configure your local endpoint in the admin UI'
        }
    }

    Write-Host ''
    Write-Info 'setup complete.'
    Write-Host '    next:  .\fcc.ps1 start     # boot the proxy'
    Write-Host '           .\fcc.ps1 claude    # open Claude Code against it'
}

function Invoke-Start {
    if (-not (Test-Path $AppDir)) { Die "not set up yet - run '.\fcc.ps1 setup' first" }
    if (Test-PortOpen) { Write-Info "proxy already listening on port $FccPort"; return }
    Write-Info "starting fcc-server on port $FccPort (log: $LogFile)"
    # Call the entry point through python rather than the generated fcc-server.exe:
    # Windows Application Control / Smart App Control blocks that unsigned shim
    # ("os error 4551"), while the signed python.exe runs the same code fine.
    $runner = Join-Path $AppDir '_run_server.py'
    Set-Content -Path $runner -Encoding utf8 -Value @(
        'from free_claude_code.cli.entrypoints import serve'
        'serve()'
    )
    $p = Start-Process -FilePath 'uv' -ArgumentList 'run', 'python', '_run_server.py' -WorkingDirectory $AppDir `
                       -RedirectStandardOutput $LogFile -RedirectStandardError "$LogFile.err" `
                       -WindowStyle Hidden -PassThru
    Set-Content -Path $PidFile -Value $p.Id
    foreach ($i in 1..40) {
        if (Test-PortOpen) {
            Write-Info "proxy is up   ->  admin UI: http://127.0.0.1:$FccPort"
            Write-Host '    pick your model there, then run: .\fcc.ps1 claude'
            return
        }
        Start-Sleep -Milliseconds 500
    }
    Write-Warn "server did not open port $FccPort within 20s - last log lines:"
    if (Test-Path $LogFile) { Get-Content $LogFile -Tail 25 }
    if (Test-Path "$LogFile.err") { Get-Content "$LogFile.err" -Tail 25 }
    exit 1
}

# Runs `claude` with exactly the Anthropic-related variables given, and nothing
# else: any of the four the caller omits is CLEARED for the child, not inherited.
# That matters in both directions - an inherited ANTHROPIC_BASE_URL would send api
# mode somewhere other than Anthropic, and an inherited ANTHROPIC_API_KEY would be
# handed to a third-party proxy in proxy mode. The shell's own values are restored
# afterwards.
function Invoke-ClaudeWith {
    param([hashtable]$Vars)
    $names = @('CLAUDE_CONFIG_DIR', 'ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY')
    $saved = @{}
    foreach ($n in $names) { $saved[$n] = [Environment]::GetEnvironmentVariable($n) }
    try {
        foreach ($n in $names) {
            if ($Vars[$n]) { Set-Item -Path "Env:$n" -Value $Vars[$n] }
            else { Remove-Item -Path "Env:$n" -ErrorAction SilentlyContinue }
        }
        & claude @Rest
    } finally {
        foreach ($n in $names) {
            if ($saved[$n]) { Set-Item -Path "Env:$n" -Value $saved[$n] }
            else { Remove-Item -Path "Env:$n" -ErrorAction SilentlyContinue }
        }
    }
}

function Invoke-Claude {
    if (-not (Have claude)) { Die "the 'claude' command is not installed" }
    if (-not (Test-PortOpen)) { Die "proxy is not running - run '.\fcc.ps1 start' first" }
    New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
    Write-Info "launching Claude Code against the local proxy (isolated profile: $ConfigDir)"
    Invoke-ClaudeWith @{
        CLAUDE_CONFIG_DIR    = $ConfigDir
        ANTHROPIC_BASE_URL   = "http://127.0.0.1:$FccPort"
        ANTHROPIC_AUTH_TOKEN = 'freecc'
    }
}

function Invoke-Api {
    if (-not (Have claude)) { Die "the 'claude' command is not installed" }
    # Key precedence: an already-set env var wins, then the saved file, then ask.
    $key = $env:ANTHROPIC_API_KEY
    if (-not $key -and (Test-Path $KeyFile)) { $key = (Get-Content $KeyFile -Raw).Trim() }
    if (-not $key) {
        Write-Host 'No API key found. Create one at https://console.anthropic.com/settings/keys'
        $secure = Read-Host 'ANTHROPIC_API_KEY (input hidden)' -AsSecureString
        $key = [System.Net.NetworkCredential]::new('', $secure).Password
        if (-not $key) { Die 'no key entered' }
        $save = Read-Host "save it to $KeyFile for next time? [y/N]"
        if ($save -match '^[yY]') {
            New-Item -ItemType Directory -Force -Path $FccHome | Out-Null
            Set-Content -Path $KeyFile -Value $key -NoNewline -Encoding utf8
            Write-Info 'saved'
        }
    }
    New-Item -ItemType Directory -Force -Path $ApiConfigDir | Out-Null
    Write-Info 'launching Claude Code on your API key - billed per token, separate from your subscription'
    # No base URL and no auth token: this must reach Anthropic directly, not the proxy.
    # Its own config dir keeps this profile apart from both the subscription login
    # and the proxied profile.
    Invoke-ClaudeWith @{
        CLAUDE_CONFIG_DIR = $ApiConfigDir
        ANTHROPIC_API_KEY = $key
    }
}

function Invoke-Status {
    Write-Host "FCC_HOME : $FccHome"
    Write-Host ("app      : " + $(if (Test-Path $AppDir) { 'present' } else { 'missing (run setup)' }))
    Write-Host ("env file : " + $(if (Test-Path $EnvFile) { $EnvFile } else { 'missing' }))
    Write-Host ("port     : $FccPort " + $(if (Test-PortOpen) { '(listening)' } else { '(closed)' }))
    if (Test-Path $PidFile) { Write-Host ("pid      : " + (Get-Content $PidFile)) }
    Write-Host "profile  : $ConfigDir   # proxied Claude Code config, separate from your main one"
    $keyState = if ($env:ANTHROPIC_API_KEY) { 'set in environment' } elseif (Test-Path $KeyFile) { "saved in $KeyFile" } else { 'not configured' }
    Write-Host "api key  : $keyState"
}

function Invoke-Stop {
    if (Test-Path $PidFile) {
        $procId = [int](Get-Content $PidFile)
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) { Stop-Process -Id $procId -Force; Write-Info "stopped pid $procId" }
        else { Write-Warn "process $procId is not running" }
        Remove-Item $PidFile -Force
    } else { Write-Warn "no running server recorded in $PidFile" }
}

function Invoke-Uninstall {
    Invoke-Stop
    if (Test-Path $KeyFile) { Write-Warn "this also deletes the saved API key at $KeyFile" }
    $a = Read-Host "delete $FccHome and everything in it? [y/N]"
    if ($a -match '^[yY]') {
        Remove-Item -Recurse -Force $FccHome
        Write-Info "removed $FccHome - your main Claude Code config was never modified"
    } else { Write-Info 'cancelled' }
}

switch ($Command) {
    'setup'     { Invoke-Setup }
    'start'     { Invoke-Start }
    'claude'    { Invoke-Claude }
    'api'       { Invoke-Api }
    'status'    { Invoke-Status }
    'stop'      { Invoke-Stop }
    'uninstall' { Invoke-Uninstall }
}
