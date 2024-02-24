# -*- coding: utf-8 -*-
#
#  Sherlock Converter
#
#  Coded/Modified/Adapted by oerlgrey
#  Based on opernHDF image source code
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

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from enigma import iServiceInformation
import NavigationInstance
from os import path, popen
from Plugins.Extensions.KravenHD.bitrate import Bitrate

class KravenHDSherlock(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = type
		self.poll_interval = 2000
		self.poll_enabled = True
		self.E2Arch = self.getE2Arch()
		self.bitrate = Bitrate()

	@cached
	def getText(self):
		if self.E2Arch in ("mipsel", "arm"):
			self.bitrate.start()
			if self.type == "videorate":
				return _("Videorate:  ") + str(self.bitrate.vcur) + _(" kbit/s")
			elif self.type == "audiorate":
				return _("Audiorate:  ") + str(self.bitrate.acur) + _(" kbit/s")
		else:
			if self.type == "videorate":
				return _("Videorate:  unknown")
			elif self.type == "audiorate":
				return _("Audiorate:  unknown")
		if self.type == "loadinfo":
			return str(self.getLoadInfo())
		if self.type == "meminfo":
			return str(self.getMemInfo())
		if self.type == "tempinfo":
			return str(self.getTempInfo())
		if self.type == "caidinfo":
			return str(self.getCaidInfo())

	text = property(getText)

	def changed(self, what):
		if what[0] is self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] is self.CHANGED_POLL:
			self.downstream_elements.changed(what)

	def getLoadInfo(self):
		try:
			out_line = popen("cat /proc/loadavg").readline()
			loadinfo = "load average: " + out_line.split(' ')[0] + " " + out_line.split(' ')[1] + " " + out_line.split(' ')[2]
			return loadinfo
		except:
			return ""

	def getMemInfo(self):
		try:
			out_line = popen("cat /proc/meminfo").readlines()
			for lidx in range(len(out_line)-1):
				tstLine = out_line[lidx].split()
				if "MemFree:" in tstLine:
					meminfo = "MemFree: " + out_line[lidx].rsplit(' ', 2)[1] + " " + out_line[lidx].rsplit(' ',1)[1]
					return meminfo
		except:
			return ""

	def getTempInfo(self):
		try:
			tempinfo = ''
			if path.exists('/proc/stb/sensors/temp0/value'):
				f = open('/proc/stb/sensors/temp0/value', 'r')
				tempinfo = f.read()
				f.close()
			elif path.exists('/proc/stb/fp/temp_sensor'):
				f = open('/proc/stb/fp/temp_sensor', 'r')
				tempinfo = f.read()
				f.close()
			elif path.exists('/proc/stb/sensors/temp/value'):
				f = open('/proc/stb/sensors/temp/value', 'r')
				tempinfo = f.read()
				f.close()
			elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				tempinfo = f.read()
				tempinfo = tempinfo[:-4]
				f.close()
			else:
				if path.exists('/proc/stb/fp/temp_sensor_avs'):
					f = open('/proc/stb/fp/temp_sensor_avs', 'r')
					tempinfo = f.read()
					f.close()
				elif path.exists('/proc/stb/power/avs'):
					f = open('/proc/stb/power/avs', 'r')
					tempinfo = f.read()
					f.close()
				elif path.exists('/proc/hisi/msp/pm_cpu'):
					for line in open('/proc/hisi/msp/pm_cpu').readlines():
						line = [ x.strip() for x in line.strip().split(':') ]
						if line[0] in 'Tsensor':
							temp = line[1].split('=')
							temp = line[1].split(' ')
							tempinfo = temp[2]

			if tempinfo and int(tempinfo.replace('\n', '')) > 0:
				mark = str('\xc2\xb0')
				return _('Temp: %s') % tempinfo.replace('\n', '').replace(' ', '') + mark + 'C\n'

		except:
			return ""

	def getCaidInfo(self):
		try:
			res = ""
			service = NavigationInstance.instance.getCurrentService()
			info = service and service.info()
			if info is not None:
				if info.getInfo(iServiceInformation.sIsCrypted):
					searchIDs =(info.getInfoObject(iServiceInformation.sCAIDs))
					for oneID in searchIDs:
						if res:
							res = res + ", "
						caid = hex(oneID).lstrip("0x")
						if (len(caid)==4):
							res = res + caid.upper()
						else:
							res = res + "0" + caid.upper()
					return "CAID: " + res
				else:
					return ""
		except:
			return ""

	def getE2Arch(self):
		try:
			from boxbranding import getImageArch
			if getImageArch() == "mips32el":
				return "mipsel"
			elif getImageArch() == "cortexa15hf-neon-vfpv4":
				return "arm"
		except ImportError:
			return "unknown"
