from dataclasses import dataclass
from typing import Optional

import openvr

@dataclass
class CurrentDeviceState:	
    index: int
    name: str
    serial: str
    charging: bool
    level: float

DEVICE_CLASS_MAP = {
    openvr.TrackedDeviceClass_HMD: "HMD",
    openvr.TrackedDeviceClass_Controller: "Controller",
    openvr.TrackedDeviceClass_GenericTracker: "Tracker",
    openvr.TrackedDeviceClass_TrackingReference: "Base Station",
    openvr.TrackedDeviceClass_DisplayRedirect: "DisplayRedirect",
}

class BatteryReader:
    is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return False

        try:
            openvr.init(openvr.VRApplication_Background)
            self.ovrSystem = openvr.VRSystem()
            self.is_initialized = True
            print("OpenVR initialized")
            return True
        except:
            print("Failed to initialize OpenVR")

        return False

    def get_device_states(self) -> Optional[list[CurrentDeviceState]]:
        if not self.is_initialized:
            return None

        if self.is_initialized:
            states = []

            for idx in range(openvr.k_unMaxTrackedDeviceCount):
                device_class = self.ovrSystem.getTrackedDeviceClass(idx)

                if device_class != openvr.TrackedDeviceClass_Invalid:
                    try:
                        device_serial = self.ovrSystem.getStringTrackedDeviceProperty(idx, openvr.Prop_SerialNumber_String)
                        is_charging = bool(self.ovrSystem.getBoolTrackedDeviceProperty(idx, openvr.Prop_DeviceIsCharging_Bool))
                        level = self.ovrSystem.getFloatTrackedDeviceProperty(idx, openvr.Prop_DeviceBatteryPercentage_Float)

                        states.append(CurrentDeviceState(
                            index=idx,
                            name=f"{device_serial} ({DEVICE_CLASS_MAP.get(device_class, 'Unknown')})",
                            serial=device_serial,
                            charging=is_charging,
                            level=level,
                        ))

                        print(idx, device_serial, f"charging={is_charging}", level)
                    except Exception as e:
                        print(repr(e))

            return states
        else:
            return None
        
    def handle_events(self):
        if not self.is_initialized:
            return
        
        evt = openvr.VREvent_t()

        while self.ovrSystem.pollNextEvent(evt):
            if evt.eventType == openvr.VREvent_Quit:
                print("Received SteamVR quit event")

                self.ovrSystem.acknowledgeQuit_Exiting()
                openvr.shutdown()

                self.is_initialized = False
                self.ovrSystem = None

                print("OpenVR uninitialized")
                return