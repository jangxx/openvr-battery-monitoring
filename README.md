# OpenVR Battery Monitoring

>Simple script to send a desktop notification if an OpenVR device starts to lose battery

## Installation

Prerequisite: Install Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/)

1. Clone repo
2. Run `uv sync` to install packages
3. Run `uv run main.py` to run the script.

Alternatively (after step 2) you can create a Desktop Shortcut to `pythonw.exe` inside `.venv/Scripts` in the project folder and give it an absolute path to `main.py` as a parameter within the Shortcut properties.
There's also an ico file in `assets/` you can use for the Shortcut.