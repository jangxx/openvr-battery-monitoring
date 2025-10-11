import sys
import os
from cx_Freeze import setup, Executable

import _version

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
	"excludes": [ "tkinter", "PIL._avif" ],
	"include_files": [
		("./assets/icon_256.png", "assets/icon_256.png"),
	],
	"zip_include_packages": "*",
	"zip_exclude_packages": [ "openvr", "desktop_notifier" ],
	"build_exe": "./dist",
}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "server"))

setup(name = "openvr_battery_monitoring",
    description = "OpenVR Battery Monitoring",
    options = { "build_exe": build_exe_options },
    executables = [
		Executable("main.py", base=base, target_name="openvr_battery_monitoring", icon = "./assets/icon.ico"),
	],
)