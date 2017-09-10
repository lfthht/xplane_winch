"""
Winch Simulator
"""
from XPLMDefs import *
from EasyDref import EasyDref
from XPLMProcessing import *
from XPLMDataAccess import *
from XPLMUtilities import *
from XPLMPlanes import *
from SandyBarbourUtilities import *
from PythonScriptMessaging import *
from XPLMPlugin import *
from XPLMMenus import *
from XPWidgetDefs import *
from XPWidgets import *
from XPStandardWidgets import *
from XPLMScenery import *
from XPLMDisplay import *
from os import path
from random import randint
from math import *

toggleWinch = 0



class PythonInterface:
	def XPluginStart(self):
		global gOutputFile

		global myMenu
		mySubMenuItem = XPLMAppendMenuItem(XPLMFindPluginsMenu(), "Winch", 0, 1)
		self.MyMenuHandlerCB = self.MyMenuHandlerCallback
		self.myMenu = XPLMCreateMenu(self, "Winch", XPLMFindPluginsMenu(), mySubMenuItem, self.MyMenuHandlerCB,   0)
		XPLMAppendMenuItem(self.myMenu, "Toggle Winch", toggleWinch, 1)

		self.Name = "WinchSim"
		self.Sig =  "JuliusBrockelmann.Python.WinchSim"
		self.Desc = "A plugin that simulates a Winch"

		self.winch_Z  = EasyDref('sim/flightmodel/forces/faxil_plug_acf', 'float')
		self.winch_L  = EasyDref('sim/flightmodel/forces/L_plug_acf', 'float')
		self.winch_M  = EasyDref('sim/flightmodel/forces/M_plug_acf', 'float')
		self.winch_N  = EasyDref('sim/flightmodel/forces/N_plug_acf', 'float')
		self.distance = EasyDref('sim/flightmodel/controls/dist', 'float')

		
		self.toggledWinch = 0
		self.rotation1 = []
		

		
		

		"""
		Register our callback for once a second.  Positive intervals
		are in seconds, negative are the negative of sim frames.  Zero
		registers but does not schedule a callback for time.
		"""
		self.FlightLoopCB = self.FlightLoopCallback
		XPLMRegisterFlightLoopCallback(self, self.FlightLoopCB, 1.0, 0)
		return self.Name, self.Sig, self.Desc



	def XPluginStop(self):
		# Unregister the callback
		XPLMUnregisterFlightLoopCallback(self, self.FlightLoopCB, 0)
		pass

	def XPluginEnable(self):
		return 1

	def XPluginDisable(self):
		pass

	def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
		pass

	def MyMenuHandlerCallback(self, inMenuRef, inItemRef):
		if (inItemRef == toggleWinch):
			self.toggledWinch = 1
			print "winch toggled"
		pass

	def FlightLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
		# The actual callback.  First we read the sim's time and the data.
		elapsed = XPLMGetElapsedTime()
		
		if self.toggledWinch == 1 and self.distance.value < 1000:
			self.winch_Z.value  = -1500
			self.winch_M.value = 100
			onground = XPLMGetDatai(XPLMFindDataRef('sim/flightmodel/failures/onground_any'))
			if onground == 1:
				#print "on ground"	
				if self.rotation1:

					lockedrotation = self.rotation1
				else:
					lockedrotation = self.rotation1
					XPLMGetDatavf(XPLMFindDataRef("sim/flightmodel/position/q"), self.rotation1, 0, 4)
				
				rotation2 = []
				XPLMGetDatavf(XPLMFindDataRef("sim/flightmodel/position/q"), rotation2, 0, 4)
				if self.distance.value < 2:
					setrotation =[rotation2[0],0.0,rotation2[2],lockedrotation[3]]
				else:
					setrotation =[rotation2[0],rotation2[1],rotation2[2],lockedrotation[3]]
				#print setrotation[1]
				XPLMSetDatavf(XPLMFindDataRef("sim/flightmodel/position/q"), setrotation, 0, 4)
		else:
			self.winch_Z.value = 0
			self.winch_M.value = 0
			#print "stays"
		if self.distance.value > 1000:
			self.toggledWinch = 0

		# set the next callback time in +n for # of seconds and -n for # of Frames
		return .01;

