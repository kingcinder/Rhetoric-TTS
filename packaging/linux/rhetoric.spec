# PyInstaller one-folder specification for the unsigned Linux rehearsal build.
# Models, caches, signing material, and user data are intentionally absent.

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

repo = Path(SPECPATH).parents[1]
datas = collect_data_files("rhetoric")
datas.extend(
    [
        (str(repo / "LICENSE"), "."),
        (str(repo / "PRIVACY.md"), "."),
        (str(repo / "EULA.md"), "."),
        (str(repo / "THIRD_PARTY_NOTICES.md"), "."),
    ]
)
# THIRD_PARTY_NOTICES.md sends readers to the license texts in
# THIRD_PARTY_LICENSES/ and to the LGPL fulfillment doc, so both must ship
# inside the frozen bundle as well. The wheel and sdist carry them through
# setuptools license-files, a mechanism PyInstaller never consults; without
# these entries the frozen artifacts omitted them entirely.
datas.extend(
    (str(path), "THIRD_PARTY_LICENSES")
    for path in sorted((repo / "THIRD_PARTY_LICENSES").iterdir())
    if path.is_file()
)
datas.append(
    (str(repo / "docs" / "release" / "LGPL_FULFILLMENT.md"), "docs/release")
)

a = Analysis(
    [str(repo / "packaging" / "linux" / "entrypoint.py")],
    pathex=[str(repo / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    excludes=["tests", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="rhetoric",
    console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, name="rhetoric")
