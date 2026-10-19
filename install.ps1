# Per-user portable installation. Never installs toolchains or changes credentials.
[CmdletBinding()]
param(
    [Alias('dry-run')][switch]$DryRun,
    [Alias('configure-only')][switch]$ConfigureOnly,
    [Alias('build-only')][switch]$BuildOnly,
    [string]$TargetHome = $env:USERPROFILE,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
if (([int]$DryRun.IsPresent + [int]$ConfigureOnly.IsPresent + [int]$BuildOnly.IsPresent) -gt 1) { throw 'Choose one mode.' }
if (-not $TargetHome) { throw 'USERPROFILE is missing; pass -TargetHome.' }
& $Python "$PSScriptRoot/configure.py" --platform windows --home $TargetHome --check
if ($LASTEXITCODE -ne 0) { throw 'Settings validation failed.' }
if ($DryRun) {
    & "$PSScriptRoot/build.ps1" -DryRun -Python $Python
    Write-Output 'Would back up and install portable binaries, settings, Codex hooks and Start Menu/startup entries in this user profile.'
    exit 0
}
if ($env:OS -ne 'Windows_NT') { throw 'This installer requires native Windows.' }
if (-not $ConfigureOnly) { & "$PSScriptRoot/build.ps1" -Python $Python }
& $Python "$PSScriptRoot/windows_build.py" --verify-release
if ($LASTEXITCODE -ne 0) { throw 'Release verification failed; configuration unchanged.' }
if ($BuildOnly) { exit 0 }
if (Get-Process -Name coucou,coucou-hook -ErrorAction SilentlyContinue) { throw 'Close Coucou from its tray icon and wait for coucou-hook processes to exit before installing.' }
$release = Join-Path $PSScriptRoot '.build/release-windows'
& $Python "$PSScriptRoot/configure.py" --platform windows --home $TargetHome --relay "$release/coucou-hook.exe" --binary "$release/coucou.exe" --bridge "$release/codex-bridge.mjs"
if ($LASTEXITCODE -ne 0) { throw 'Configuration failed.' }
Write-Output 'Installed. Start Coucou from the Start Menu; it will also start at login. Review /hooks in Codex.'
Write-Output 'Restore with: python restore.py BACKUP_PATH --dry-run (then omit --dry-run with Coucou closed).'
