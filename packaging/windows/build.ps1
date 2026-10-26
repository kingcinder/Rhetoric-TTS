param(
    [string]$Version = "1.5.0",
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$dist = Join-Path $repo "dist\Rhetoric"
$pyinstaller = Get-Command pyinstaller -ErrorAction Stop
$iscc = Get-Command iscc -ErrorAction Stop

Push-Location $repo
try {
    & $Python scripts/manage_install.py bootstrap --skip-doctor
    & $Python -m pip install pyinstaller
    & $pyinstaller.Source --noconfirm --clean --windowed --name Rhetoric --distpath (Join-Path $repo "dist") (Join-Path $repo "packaging\windows\entrypoint.py")
    & $iscc.Source "/DProductVersion=$Version" "/DSourceDir=$dist" (Join-Path $repo "packaging\windows\Rhetoric.iss")
} finally {
    Pop-Location
}
