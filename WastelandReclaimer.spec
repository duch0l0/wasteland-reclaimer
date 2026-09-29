# -*- mode: python ; coding: utf-8 -*-
# Сборка одного исполняемого файла игры (PyInstaller):
#   Windows:  .venv\Scripts\pyinstaller WastelandReclaimer.spec   -> dist\WastelandReclaimer.exe
#   Linux:    .venv/bin/pyinstaller WastelandReclaimer.spec       -> dist/WastelandReclaimer
# В exe попадают только assets/ и data/ — исходники графики и звука (npc/, sounds/,
# wasteland town/) игре не нужны. Сохранения игра пишет в saves/ рядом с exe.

a = Analysis(
    ["main.py"],
    pathex=["."],
    datas=[("assets", "assets"), ("data", "data")],
    hiddenimports=[],
    excludes=["tkinter", "numpy", "unittest", "pydoc", "email", "xml"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WastelandReclaimer",
    icon="build_tools/icon.ico",
    console=False,   # без чёрного окна консоли; ошибки — в crash.log рядом с exe
    upx=False,
    strip=False,
    debug=False,
)
