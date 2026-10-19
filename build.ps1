# Run in x64 Native Tools / Developer PowerShell (Visual Studio C++ + Windows SDK).
[CmdletBinding()]
param(
    [Alias('prepare-only')][switch]$PrepareOnly,
    [Alias('dry-run')][switch]$DryRun,
    [switch]$Bundle,
    [string]$Archive,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$buildArgs = @("$PSScriptRoot/windows_build.py")
if ($PrepareOnly) { $buildArgs += '--prepare-only' }
if ($DryRun) { $buildArgs += '--dry-run' }
if ($Bundle) { $buildArgs += '--bundle' }
if ($Archive) { $buildArgs += @('--archive', $Archive) }
& $Python @buildArgs
if ($LASTEXITCODE -ne 0) { throw "Windows build failed (exit $LASTEXITCODE)." }
