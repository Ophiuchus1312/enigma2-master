from Screen import Screen
from MessageBox import MessageBox
from Components.config import config
import Screens.Standby

class PowerLost(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.showMessageBox()

	def showMessageBox(self):
		message = _("Your STB_BOX was not shutdown properly.\n\n"
					"Do you want to put it in %s?") % config.usage.shutdownNOK_action.getValue()
		self.session.openWithCallback(self.MsgBoxClosed, MessageBox, message, MessageBox.TYPE_YESNO, timeout = 60, default = True)

	def MsgBoxClosed(self, ret):
		if ret:
			if config.usage.shutdownNOK_action.getValue() == 'deepstandby':
				self.session.open(Screens.Standby.TryQuitMainloop, 1)
			elif not Screens.Standby.inStandby:
				self.session.open(Screens.Standby.Standby)

		self.close()
