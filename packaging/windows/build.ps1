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
    $pyiArgs = @("--noconfirm", "--clean", "--windowed", "--name", "Rhetoric", "--distpath", (Join-Path $repo "dist"))
    # Mirror packaging/linux/rhetoric.spec: the LGPL license texts in
    # THIRD_PARTY_LICENSES and the fulfillment doc must be inside the
    # frozen bundle, or the shipped notices point at files the
    # installer does not contain. Rhetoric.iss wraps the dist folder.
    Get-ChildItem (Join-Path $repo "THIRD_PARTY_LICENSES") -File | ForEach-Object {
        $pyiArgs += @("--add-data", "$($_.FullName);THIRD_PARTY_LICENSES")
    }
    $pyiArgs += @("--add-data", "$(Join-Path $repo 'docs\release\LGPL_FULFILLMENT.md');docs\release")
    $pyiArgs += (Join-Path $repo "packaging\windows\entrypoint.py")
    & $pyinstaller.Source @pyiArgs
    & $iscc.Source "/DProductVersion=$Version" "/DSourceDir=$dist" (Join-Path $repo "packaging\windows\Rhetoric.iss")
} finally {
    Pop-Location
}
