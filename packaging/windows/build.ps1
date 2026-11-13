param(
    [string]$Version = "1.5.0",
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..\")
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
    # Mirror the spec's collect_data_files("rhetoric") and its
    # root-level docs. Without the package data, the frozen bundle had
    # NO EULA.md anywhere: the first-run EULA lookup returned None,
    # run_eula_acceptance returned False without ever showing its
    # dialog, and Rhetoric.exe exited silently in ~3s on a fresh
    # profile (diagnosed in the Windows guest, 2026-11-12: copying
    # EULA.md into the install root made the same exe open the
    # "Rhetoric - License Agreement" dialog and stay alive).
    $pyiArgs += @("--collect-data", "rhetoric")
    foreach ($rootDoc in @("LICENSE", "PRIVACY.md", "EULA.md", "THIRD_PARTY_NOTICES.md")) {
        $pyiArgs += @("--add-data", "$(Join-Path $repo $rootDoc);.")
    }
    $pyiArgs += (Join-Path $repo "packaging\windows\entrypoint.py")
    & $pyinstaller.Source @pyiArgs
    # The installer writes this digest into eula_acceptance.json (see
    # Rhetoric.iss [Code]) so an installer-accepted EULA is not asked
    # again by the app's first-run dialog.
    # PyInstaller 6 onedir layout: every data lands under _internal, and
    # sys._MEIPASS points there - that is where the app looks.
    foreach ($required in @("_internal\EULA.md", "_internal\rhetoric\EULA.md")) {
        if (-not (Test-Path (Join-Path $dist $required))) {
            throw "Frozen bundle is missing $required - the first-run EULA gate cannot find its text"
        }
    }
    $eulaHash = (Get-FileHash (Join-Path $repo "EULA.md") -Algorithm SHA256).Hash.ToLowerInvariant()
    & $iscc.Source "/DProductVersion=$Version" "/DSourceDir=$dist" "/DEulaSha256=$eulaHash" (Join-Path $repo "packaging\windows\Rhetoric.iss")
} finally {
    Pop-Location
}
