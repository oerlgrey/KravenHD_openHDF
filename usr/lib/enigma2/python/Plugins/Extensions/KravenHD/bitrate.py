# -*- coding: utf-8 -*-

#  Bitrate
#
#  Coded/Modified/Adapted by oerlgrey
#  Based on openHDF image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact me at ochzoetna@gmail.com

from enigma import eConsoleAppContainer, iServiceInformation
import NavigationInstance

class Bitrate:
	def __init__(self):
		self.remainingdata = ""
		self.running = False
		self.clearValues()
		self.datalines = []
		self.container = eConsoleAppContainer()
		self.container.dataAvail.append(self.dataAvail)
		self.E2Arch = self.getE2Arch()

	def start(self):
		if self.E2Arch == "mipsel":
			binary = "/usr/lib/enigma2/python/Plugins/Extensions/KravenHD/bitrate_mipsel "
		elif self.E2Arch == "arm":
			binary = "/usr/lib/enigma2/python/Plugins/Extensions/KravenHD/bitrate_arm "
		if self.running:
			return
		service = NavigationInstance.instance.getCurrentService()
		if service:
			adapter = 0
			demux = 0
			try:
				stream = service.stream()
				if stream:
					streamdata = stream.getStreamingData()
					if streamdata:
						if 'demux' in streamdata:
							demux = streamdata["demux"]
						if 'adapter' in streamdata:
							adapter = streamdata["adapter"]
			except:
				pass
			info = service.info()
			vpid = info.getInfo(iServiceInformation.sVideoPID)
			apid = info.getInfo(iServiceInformation.sAudioPID)
			cmd = str(binary)
			cmd += str(adapter)
			cmd += " "
			cmd += str(demux)
			cmd += " "
			cmd += str(vpid)
			cmd += " "
			cmd += str(apid)
			self.running = True
			self.container.execute(cmd)

	def clearValues(self):
		self.vmin = 0
		self.vmax = 0
		self.vavg = 0
		self.vcur = 0
		self.amin = 0
		self.amax = 0
		self.aavg = 0
		self.acur = 0

	def stop(self):
		self.container.kill()
		self.remainingdata = ""
		self.clearValues()
		self.running = False

	def dataAvail(self, str):
		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		newlines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(newlines[-1]):
			#remember this data for next time
			self.remainingdata = newlines[-1]
			newlines = newlines[0:-1]
		else:
			self.remainingdata = ""

		for line in newlines:
			if len(line):
				self.datalines.append(line)
		if len(self.datalines) >= 2:
			try:
				self.vmin, self.vmax, self.vavg, self.vcur = self.datalines[0].split(' ')
				self.amin, self.amax, self.aavg, self.acur = self.datalines[1].split(' ')
			except:
				self.clearValues()
			self.datalines = []

	def getE2Arch(self):
		try:
			from boxbranding import getImageArch
			if getImageArch() == "mips32el":
				return "mipsel"
			elif getImageArch() == "cortexa15hf-neon-vfpv4":
				return "arm"
		except:
			return "unknown"
