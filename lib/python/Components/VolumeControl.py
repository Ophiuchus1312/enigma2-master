from enigma import eDVBVolumecontrol, eTimer
from Tools.Profile import profile
from Screens.Volume import Volume
from Screens.Mute import Mute
from GlobalActions import globalActionMap
from config import config, ConfigSubsection, ConfigInteger
from Components.HdmiCec import HdmiCec

profile("VolumeControl")
#TODO .. move this to a own .py file
class VolumeControl:
	instance = None
	"""Volume control, handles volUp, volDown, volMute actions and display
	a corresponding dialog"""
	def __init__(self, session):
		global globalActionMap
		globalActionMap.actions["volumeUp"]=self.volUp
		globalActionMap.actions["volumeDown"]=self.volDown
		globalActionMap.actions["volumeMute"]=self.volMute

		assert not VolumeControl.instance, "only one VolumeControl instance is allowed!"
		VolumeControl.instance = self

		config.audio = ConfigSubsection()
		config.audio.volume = ConfigInteger(default = 50, limits = (0, 100))

		self.volumeDialog = session.instantiateDialog(Volume)
		self.muteDialog = session.instantiateDialog(Mute)

		self.hideVolTimer = eTimer()
		self.hideVolTimer.callback.append(self.volHide)

		vol = config.audio.volume.getValue()
		self.volumeDialog.setValue(vol)
		self.volctrl = eDVBVolumecontrol.getInstance()
		self.volctrl.setVolume(vol, vol)

	def volSave(self):
		if self.volctrl.isMuted():
			config.audio.volume.setValue(0)
		else:
			config.audio.volume.setValue(self.volctrl.getVolume())
		config.audio.volume.save()

	def volUp(self):
		if HdmiCec.instance.volumeForwardingEnabled: return
		self.setVolume(+1)

	def volDown(self):
		if HdmiCec.instance.volumeForwardingEnabled: return
		self.setVolume(-1)

	def setVolume(self, direction):
		oldvol = self.volctrl.getVolume()
		if direction > 0:
			self.volctrl.volumeUp()
		else:
			self.volctrl.volumeDown()
		is_muted = self.volctrl.isMuted()
		vol = self.volctrl.getVolume()
		self.volumeDialog.show()
		if is_muted:
			self.volMute() # unmute
		elif not vol:
			self.volMute(False, True) # mute but dont show mute symbol
		if self.volctrl.isMuted():
			self.volumeDialog.setValue(0)
		else:
			self.volumeDialog.setValue(self.volctrl.getVolume())
		self.volSave()
		self.hideVolTimer.start(3000, True)

	def volHide(self):
		self.volumeDialog.hide()

	def volMute(self, showMuteSymbol=True, force=False):
		if HdmiCec.instance.volumeForwardingEnabled: return
		vol = self.volctrl.getVolume()
		if vol or force:
			self.volctrl.volumeToggleMute()
			if self.volctrl.isMuted():
				if showMuteSymbol:
					self.muteDialog.show()
				self.volumeDialog.setValue(0)
			else:
				self.muteDialog.hide()
				self.volumeDialog.setValue(vol)
