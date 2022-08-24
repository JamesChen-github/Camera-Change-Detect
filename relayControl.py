'''
TODO:

USAGE:
	create relay objects with their id 
	for the return value of all operations, 0 is success, and 1 is fail
'''

from ctypes import *
import platform

driver = "./usb_relay_device"

class RELAY(Structure):
	pass

RELAY._fields_ = [
	("serial_number", POINTER(c_ubyte)),
    ("device_path", POINTER(c_byte)),
    ("type", c_int),
    ("next", POINTER(RELAY))
]

exitStatus = 0
if sizeof(c_voidp) != 4:
	print('Seems like you are using 64-bit Python.\nMust run with 32-bit'
	' Python!')

if platform.system() != 'Windows':
	print('This program can only run on a Windows machine!')

try:
	usbRelay = CDLL(driver)
except Exception as e:
	raise e

searchDevice = usbRelay.usb_relay_device_enumerate
searchDevice.restype = POINTER(RELAY)

openDevice = usbRelay.usb_relay_device_open
openDevice.restype = c_int

openDeviceID = usbRelay.usb_relay_device_open_with_serial_number
openDeviceID.restype = c_int

openAllChannel = usbRelay.usb_relay_device_open_all_relay_channel
openAllChannel.argtypes = [c_int]
openAllChannel.restype = c_int

openOneChannel = usbRelay.usb_relay_device_open_one_relay_channel
openOneChannel.argtypes = [c_int, c_int]
openOneChannel.restype = c_int

closeAllChannel = usbRelay.usb_relay_device_close_all_relay_channel
closeAllChannel.argtypes = [c_int]
closeAllChannel.restype = c_int

closeOneChannel = usbRelay.usb_relay_device_close_one_relay_channel
closeOneChannel.argtypes = [c_int, c_int]
closeOneChannel.restype = c_int

deviceStatus = usbRelay.usb_relay_device_get_status
deviceStatus.argtypes = [c_int, POINTER(c_uint)]
deviceStatus.restype = c_int

class Relay:
	def __init__(self, *ID):
		self._ID = ID
		self.__handler = None
		usbRelay.usb_relay_init()

	@property
	def ID(self):
		return self._ID
	
	def openRelay(self):
		if self._ID:
			self.__handler = openDeviceID(byref(create_string_buffer(ID.
				encode())), len(ID))
			if not self.__handler == 0:
				print("Initialization Failed!\nPlease check connection for "
					"device {}, make sure no other softwares are connected."
					.format(self._ID))
				raise
		else:
			try:
				self.__handler = openDevice(byref(searchDevice()[0]))
			except ValueError as e:
				print("No usb relay found!\nPlease recheck the connection, "
					"and make sure no other softwares are connected.")
				raise e
			except Exception as e:
				print("Some other error occured")
				raise e


	def openAll(self):
		'''
		open all the relay connections
		return -- 0: success, 1: error
		'''
		self.openRelay()
		result = openAllChannel(self.__handler)
		usbRelay.usb_relay_device_close(self.__handler)
		return result

	 
	def openChannel(self, channel):
		'''
		open relay channels according to index number
		for 4 channel relay, the index is from 4-8
		return -- 0: success, 1: error, 2: index out of range
		'''
		self.openRelay()
		result = openOneChannel(self.__handler, channel)
		print("openChannel: " + str(channel))
		usbRelay.usb_relay_device_close(self.__handler)
		return result

	 
	def closeAll(self):
		'''
		close all the relay connections
		return -- 0: success, 1: error
		'''
		self.openRelay()
		result = closeAllChannel(self.__handler)
		usbRelay.usb_relay_device_close(self.__handler)
		return result

	 
	def closeChannel(self, channel):
		'''
		close relay channels according to index number
		for 4 channel relay, the index is from 4-8
		return -- 0: success, 1: error, 2: index out of range
		'''
		self.openRelay()
		result = closeOneChannel(self.__handler, channel)
		print("closeChannel: " + str(channel))
		usbRelay.usb_relay_device_close(self.__handler)
		return result

	 
	def getStatus(self, channel = 0):
		'''
		return the array of relay channels that are currently open
		if channel is specified, return the status of the channel
		1 -- open; 0 -- close
		return 1 if error
		'''
		self.openRelay()
		statusBits = c_uint(0)
		# statusBits passed as a pointer
		result = deviceStatus(self.__handler, byref(statusBits))

		# error
		if result:
			return 1

		result = []
		statusBits = format(statusBits.value, '008b')
		if channel:
			return int(statusBits[8-channel])

		for i in range(1, 9):
			if int(statusBits[8-i]):
				result.append(i)

		usbRelay.usb_relay_device_close(self.__handler)
		return result

		
	def closeDevice(self):
		'''close the connection to the relay'''
		usbRelay.usb_relay_exit()



if __name__ == '__main__':
	print("Usage:\n\tRelay(RELAY_NAME) - to connect to a specified relay"
		"\n\tRelay()           - to search and connect to a relay\n\n\tV"
		"ariables:\n\t\tID\n\tControls: \n\t\topenAll(), closeAll(), ope"
		"nChannel(CHANNEL), closeChannel(CHANNEL), \n\t\tgetStatus(), ge"
		"tStatus(CHANNEL), closeDevice()")
