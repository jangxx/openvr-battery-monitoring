import asyncio
from dataclasses import dataclass
import signal
import threading
import sys
import os
from pathlib import Path

import pystray
from PIL import Image
from desktop_notifier import DesktopNotifier, DEFAULT_SOUND, Icon
from playsound3 import playsound

from lib.battery_reader import BatteryReader, CurrentDeviceState
from lib.config import CONFIG_DIR, Config
from lib.ovrt_notifier import OvrtIcon, OvrtNotifier

# determine if we are frozen with cx_freeze or running normally
if getattr(sys, 'frozen', False):
    # The application is frozen
    SCRIPT_DIR = os.path.dirname(sys.executable)
    IS_FROZEN = True
else:
    # The application is not frozen
    SCRIPT_DIR = os.path.dirname(__file__)
    IS_FROZEN = False

# create config dir if it doesn't exist
Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)

desktop_notifier = DesktopNotifier(app_name="Battery Monitor")
ovrt_notifier = OvrtNotifier()
battery_reader = BatteryReader()
config = Config()

@dataclass
class DeviceState:
    state: CurrentDeviceState
    level_direction: int = 0

device_states: dict[int, DeviceState] = {}
muted_devices = set(config.data.muted_devices)
quit_event = threading.Event()

trayicon = None

def relpath(p):
    return os.path.normpath(os.path.join(SCRIPT_DIR, p))

def toggle_device_mute(dev: CurrentDeviceState):
    if dev.serial in muted_devices:
        muted_devices.remove(dev.serial)
    else:
        muted_devices.add(dev.serial)

    config.data.muted_devices = list(muted_devices)
    config.save()

def generate_devices_submenu():
    yield pystray.MenuItem("Uncheck devices to disable notifications", action=None, enabled=False)
    yield pystray.Menu.SEPARATOR

    def make_action(dev: CurrentDeviceState):
        def action():
            toggle_device_mute(dev)

        return action
    
    def make_checked(dev: CurrentDeviceState):
        def checked(item):
            return dev.serial not in muted_devices

        return checked

    for dev_state in device_states.values():
        yield pystray.MenuItem(
            text=dev_state.state.name,
            radio=True,
            action=make_action(dev_state.state),
            checked=make_checked(dev_state.state),
        )

def generate_notifications_submenu():
    def toggle_desktop_notifications():
        config.data.notifications.desktop = not config.data.notifications.desktop
        config.save()

    def toggle_ovrt_notifications():
        config.data.notifications.ovrt = not config.data.notifications.ovrt
        config.save()

    def toggle_notification_sound():
        config.data.notifications.play_sound = not config.data.notifications.play_sound
        config.save()

    yield pystray.MenuItem(
        text="Notification Sound",
        checked=lambda item: config.data.notifications.play_sound,
        action=lambda item: toggle_notification_sound(),
    )

    yield pystray.MenuItem(
        text="Desktop Notifications",
        checked=lambda item: config.data.notifications.desktop,
        action=lambda item: toggle_desktop_notifications(),
    )

    yield pystray.MenuItem(
        text="OVRT Notifications",
        checked=lambda item: config.data.notifications.ovrt,
        action=lambda item: toggle_ovrt_notifications(),
    )

def generate_menu():
    if not battery_reader.is_initialized:
        yield pystray.MenuItem("Not connected to SteamVR", action=None, enabled=False)
    else:
        yield pystray.MenuItem("Devices", action=pystray.Menu(generate_devices_submenu))
        yield pystray.MenuItem("Notifications", action=pystray.Menu(generate_notifications_submenu))

    yield pystray.Menu.SEPARATOR

    yield pystray.MenuItem("Exit", action=exit_program)

trayicon = pystray.Icon("ovr_battery_monitoring", title="OpenVR Battery Monitoring", menu=pystray.Menu(generate_menu))
trayicon.icon = Image.open(relpath("assets/icon_256.png"))

desktop_notification_icon = Icon(path=Path(relpath("assets/icon_256.png")))
ovrt_notification_icon = OvrtIcon(relpath("assets/icon_ovrt.png"))
# notification_sound = Sound(path=Path(relpath("assets/low_battery.mp3")))

def exit_program():
    quit_event.set()
    trayicon.stop()

async def main():
    while not quit_event.is_set():
        just_initialized = battery_reader.initialize()

        if just_initialized:
            if config.data.notifications.desktop:
                await desktop_notifier.send(
                    title="Montior started",
                    sound=DEFAULT_SOUND if config.data.notifications.play_sound else None,
                    message=f"Battery monitor has started.",
                    icon=desktop_notification_icon,
                )

            if config.data.notifications.ovrt:
                # startup notification sound is not needed
                # if config.data.notifications.play_sound:
                    # playsound(relpath("assets/low_battery.mp3"), block=False)

                await ovrt_notifier.send_notification(
                    title="Monitor started",
                    body="Battery monitor has started.",
                    icon=ovrt_notification_icon,
                )

        states = battery_reader.get_device_states()

        if states is not None:
            for current_state in states:
                if current_state.index not in device_states:
                    device_states[current_state.index] = DeviceState(state=current_state)

                is_discharging = False
                dev_state = device_states[current_state.index]

                # simple case, device actually reports the state properly
                if dev_state.state.charging and not current_state.charging:
                    is_discharging = True

                if dev_state.state.level > current_state.level:
                    if dev_state.level_direction > 0:
                        # was going up before but now it's decreasing
                        is_discharging = True
                    
                    dev_state.level_direction = -1
                elif dev_state.state.level < current_state.level:
                    dev_state.level_direction = 1 # battery level is increasing

                dev_state.state = current_state

                if is_discharging and current_state.serial not in muted_devices:
                    if config.data.notifications.desktop:
                        await desktop_notifier.send(
                            title="Battery warning",
                            sound=DEFAULT_SOUND if config.data.notifications.play_sound else None,
                            message=f"Device {dev_state.state.name} just started discharging!",
                            icon=desktop_notification_icon,
                        )

                    if config.data.notifications.ovrt:
                        if config.data.notifications.play_sound:
                            playsound(relpath("assets/low_battery.mp3"), block=False)

                        await ovrt_notifier.send_notification(
                            title="Battery warning",
                            body=f"Device {dev_state.state.name} just started discharging!",
                            icon=ovrt_notification_icon,
                        )
        else:
            device_states.clear()

        trayicon.update_menu()

        # keep an event loop running to react to steamvr closing
        for _ in range(config.data.update_interval * 4):
            battery_reader.handle_events()

            if quit_event.is_set():
                 return

            await asyncio.sleep(0.25)

def setup(icon):
    icon.visible = True

    asyncio.run(main())

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    trayicon.run(setup=setup)