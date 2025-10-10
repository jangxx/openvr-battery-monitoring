import asyncio
from dataclasses import dataclass
import signal
import threading
import sys
import os
from pathlib import Path

import pystray
from PIL import Image

from desktop_notifier import DesktopNotifier, DEFAULT_SOUND, Icon, Sound
from battery_reader import BatteryReader

# determine if we are frozen with cx_freeze or running normally
if getattr(sys, 'frozen', False):
	# The application is frozen
	SCRIPT_DIR = os.path.dirname(sys.executable)
	IS_FROZEN = True
else:
	# The application is not frozen
	SCRIPT_DIR = os.path.dirname(__file__)
	IS_FROZEN = False


notifier = DesktopNotifier(app_name="Battery Monitor")
battery_reader = BatteryReader()

@dataclass
class DeviceState:
    charging: bool
    level: float
    level_direction: int = 0

device_states: dict[int, DeviceState] = {}
quit_event = threading.Event()

trayicon = None

def relpath(p):
	return os.path.normpath(os.path.join(SCRIPT_DIR, p))

def generate_menu():
	yield pystray.MenuItem("Exit", action=exit_program)

traymenu = pystray.Menu(generate_menu)

trayicon = pystray.Icon("ovr_battery_monitoring", title="OpenVR Battery Monitoring", menu=traymenu)
trayicon.icon = Image.open(relpath("assets/icon_256.png"))

notification_icon = Icon(path=Path(relpath("assets/icon_256.png")))
# notification_sound = Sound(path=Path(relpath("assets/uh_oh.wav")))

def exit_program():
	quit_event.set()
	trayicon.stop()

async def main():
    while not quit_event.is_set():
        just_initialized = battery_reader.initialize()

        if just_initialized:
            await notifier.send(
                title="Montior started",
                sound=DEFAULT_SOUND,
                message=f"Battery monitor has started.",
                icon=notification_icon,
            )

        levels = battery_reader.get_devices_battery_levels()

        if levels is not None:
            for idx, name, is_charging, level in levels:
                if idx not in device_states:
                    device_states[idx] = DeviceState(charging=is_charging, level=level)

                is_discharging = False                

                # simple case, device actually reports the state properly
                if device_states[idx].charging and not is_charging:
                    is_discharging = True

                device_states[idx].charging = is_charging

                if device_states[idx].level > level:
                    if device_states[idx].level_direction > 0:
                        # was going up before but now it's decreasing
                        is_discharging = True
                    
                    device_states[idx].level_direction = -1
                elif device_states[idx].level < level:
                    device_states[idx].level_direction = 1 # battery level is increasing

                device_states[idx].level = level

                if is_discharging:
                    await notifier.send(
                        title="Battery warning",
                        sound=DEFAULT_SOUND,
                        message=f"Device {name} just started discharging!",
                        icon=notification_icon,
                    )


        # keep an event loop running to react to steamvr closing
        for i in range(10):
            battery_reader.handle_events()

            if quit_event.is_set():
                 return

            await asyncio.sleep(1)

def setup(icon):
    icon.visible = True

    asyncio.run(main())

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	trayicon.run(setup=setup)