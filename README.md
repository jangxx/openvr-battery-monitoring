# OpenVR Battery Monitoring

> Simple script to send a desktop notification if an OpenVR device stops charging.

## Why?

Many people use powerbanks connected to tracked devices in SteamVR (e.g. wireless HMDs, Vive trackers, etc).
A common problem is either the cable disconnecting from the powerbank for some reason or the powerbank running out of charge which both lead to the device not getting charged anymore without the user noticing.

This tool aims to solve this problem by monitoring the charging state of devices that expose it and showing a notification whenver a device goes from charging to not charging.

## Installation

1. Go to the [Latest release](https://github.com/jangxx/openvr-battery-monitoring/releases/latest) and download the zip file containing the executable.
2. Unzip the file to wheverever you like and then run the included `openvr_battery_monitoring.exe`.

The script will run in the background and put a little icon into your system tray which you can use to quit the app and disable notifications for certain devices.
As soon as SteamVR is launched it will connect to it and monitor connected devices.
Once SteamVR quits it will keep running and automatically re-connect once it's launched again.

### Updating

Simply delete the downloaded files, download the latest version and run them.
The configuration is stored in `%localappdata%` and newer versions of the script are compatible with older versions of the configuration.

## Troubleshooting

### My device doesn't show up in the device list/is not tracked

If the device shows up in the SteamVR interface but not in the devices list it most likely doesn't expose its charging state to SteamVR.
You can check if it does by hovering over the device in the SteamVR window.
If you see a little battery icon, SteamVR can see the charging state and so can this app, otherwise the device does not expose it's charging state to SteamVR.

## Running from source

Prerequisite: Install Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/)

1. Clone repo
2. Run `uv sync` to install packages
3. Run `uv run main.py` to run the script.

Alternatively (after step 2) you can create a Desktop Shortcut to `pythonw.exe` inside `.venv/Scripts` in the project folder and give it an absolute path to `main.py` as a parameter within the Shortcut properties.

There's also an ico file in `assets/` you can use for the Shortcut.

# Attribution

- Low-battery.mp3 by oysterqueen -- https://freesound.org/s/582986/ -- License: Creative Commons 0