import openvr

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

	def get_devices_battery_levels(self):
		if not self.is_initialized:
			return None

		if self.is_initialized:
			levels = []

			for idx in range(openvr.k_unMaxTrackedDeviceCount):
				device_class = self.ovrSystem.getTrackedDeviceClass(idx)

				if device_class != openvr.TrackedDeviceClass_Invalid:
					try:
						device_name = self.ovrSystem.getStringTrackedDeviceProperty(idx, openvr.Prop_SerialNumber_String)
						is_charging = bool(self.ovrSystem.getBoolTrackedDeviceProperty(idx, openvr.Prop_DeviceIsCharging_Bool))
						level = self.ovrSystem.getFloatTrackedDeviceProperty(idx, openvr.Prop_DeviceBatteryPercentage_Float)

						levels.append((idx, device_name, is_charging, level))

						print(idx, device_name, f"charging={is_charging}", level)
					except openvr.error_code.TrackedProp_UnknownProperty:
						pass

			return levels
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