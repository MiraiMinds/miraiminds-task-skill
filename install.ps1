# Installs the MiraiMinds /task skill on Windows.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 [-Source <repo url>]
param([string]$Source = "")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$team = Get-Content (Join-Path $here "skill\config\team.json") -Raw | ConvertFrom-Json

function Fail($reason, $detail) {
    $contact = $team.emergency_contact
    @{ ok = $false; reason = $reason; detail = "$detail"; emergency = $contact } | ConvertTo-Json -Compress
    exit 1
}

# 1. uv (installs Python and the tracker connector; no admin rights needed)
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
foreach ($candidate in @("$env:USERPROFILE\.local\bin\uv.exe", "$env:USERPROFILE\.cargo\bin\uv.exe")) {
    if (-not $uv -and (Test-Path $candidate)) { $uv = $candidate }
}
if (-not $uv) {
    Write-Host "Installing uv..."
    try {
        powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex" | Out-Host
    } catch { Fail "uv_install_failed" $_ }
    foreach ($candidate in @("$env:USERPROFILE\.local\bin\uv.exe", "$env:USERPROFILE\.cargo\bin\uv.exe")) {
        if (-not $uv -and (Test-Path $candidate)) { $uv = $candidate }
    }
    if (-not $uv) { Fail "uv_not_found" "uv was installed but could not be found" }
}

# 2. The tracker connector, installed once so Claude doesn't wait for a download on every start
Write-Host "Installing the tracker connector ($($team.mcp_server_package))..."
& $uv tool install --force --compile-bytecode $team.mcp_server_package | Out-Host
if ($LASTEXITCODE -ne 0) { Fail "connector_install_failed" "uv tool install exited with $LASTEXITCODE" }

$toolDir = (& $uv tool dir).Trim()
$python = Join-Path $toolDir "plane-mcp-server\Scripts\python.exe"
if (-not (Test-Path $python)) { Fail "connector_python_missing" $python }

# 3. Skill files, helper, safety rules
# (Windows PowerShell drops empty arguments, so --source is only passed when there is one.)
$installArgs = @((Join-Path $here "installer\install.py"), "--uv", $uv)
if ($Source) { $installArgs += @("--source", $Source) }
& $python @installArgs
exit $LASTEXITCODE
