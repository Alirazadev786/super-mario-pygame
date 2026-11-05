import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
STAGING = os.path.join(HOME, "Desktop", "SuperMario", "final_build")
APP = os.path.join(STAGING, "SuperMario.app")
CONTENTS = os.path.join(APP, "Contents")
MACOS = os.path.join(CONTENTS, "MacOS")
RES = os.path.join(CONTENTS, "Resources")
VENV = os.path.join(RES, "venv")

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "super_mario.py")
ICON = os.path.join(BASE, "icon.icns")

for d in [STAGING, MACOS, RES]:
    os.makedirs(d, exist_ok=True)

shutil.copy2(SOURCE, os.path.join(RES, "super_mario.py"))
if os.path.exists(ICON):
    shutil.copy2(ICON, os.path.join(RES, "icon.icns"))

# README (short)
with open(os.path.join(RES, "README.md"), "w") as f:
    f.write("# SuperMario\n\nPygame platformer. Controls: Arrows = move, Space = jump, Esc = menu.\n")

# launcher
launcher = os.path.join(MACOS, "SuperMario")
with open(launcher, "w") as f:
    f.write('#!/bin/bash\n')
    f.write('cd "$(dirname "$0")/../Resources"\n')
    f.write('exec ./venv/bin/python super_mario.py\n')
os.chmod(launcher, 0o755)

# Info.plist
plist = os.path.join(CONTENTS, "Info.plist")
has_icon = os.path.exists(os.path.join(RES, "icon.icns"))
with open(plist, "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
    f.write('<plist version="1.0">\n<dict>\n')
    f.write('    <key>CFBundleExecutable</key>\n    <string>SuperMario</string>\n')
    f.write('    <key>CFBundleIdentifier</key>\n    <string>com.supermario.game</string>\n')
    f.write('    <key>CFBundleName</key>\n    <string>SuperMario</string>\n')
    f.write('    <key>CFBundlePackageType</key>\n    <string>APPL</string>\n')
    f.write('    <key>CFBundleShortVersionString</key>\n    <string>2.0</string>\n')
    f.write('    <key>CFBundleVersion</key>\n    <string>2</string>\n')
    if has_icon:
        f.write('    <key>CFBundleIconFile</key>\n    <string>icon.icns</string>\n')
    f.write('</dict>\n</plist>\n')

# venv + pygame
if not os.path.exists(os.path.join(VENV, "bin", "python")):
    subprocess.check_call([sys.executable, "-m", "venv", VENV])
subprocess.check_call([os.path.join(VENV, "bin", "pip"), "install", "--quiet", "pygame"])

# Applications symlink
apps_link = os.path.join(STAGING, "Applications")
if not os.path.islink(apps_link):
    os.symlink("/Applications", apps_link)

# DMG
dmg = os.path.join(HOME, "Desktop", "SuperMario", "super_mario.dmg")
if os.path.exists(dmg):
    os.remove(dmg)
subprocess.check_call(["hdiutil", "create", "-volname", "SuperMario", "-srcfolder", STAGING, "-ov", "-format", "UDZO", dmg])
print("BUILD_DONE:", dmg)
