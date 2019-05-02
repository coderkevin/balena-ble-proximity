from bluepy.btle import Scanner, DefaultDelegate
from threading import Thread
from time import sleep

# Adtypes according to https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
ADTYPE_COMPLETE_LOCAL_NAME = 0x09

class Neighbor():
	def __init__(self, dev):
		self.addr = dev.addr
		self.addrType = dev.addrType
		self.rssi = dev.rssi
		self.localName = None

		for (adtype, desc, value) in dev.getScanData():
			if adtype == ADTYPE_COMPLETE_LOCAL_NAME:
				self.localName = value

	def __lt__(self, other):
		return self.rssi < other.rssi

class BTScan(Thread):
	def __init__(self, addresses, onScan, timeout=1, delay=9):
		super().__init__()
		self.timeout = timeout
		self.delay = delay
		self.addresses = addresses
		self.onScan = onScan

	def run(self):
		while True:
			print("Scanning bluetooth devices...")
			scanner = Scanner()
			devices = scanner.scan(self.timeout)
			neighbors = []
			for dev in devices:
				if dev.addr in self.addresses:
					neighbors.append(Neighbor(dev))

			self.onScan(neighbors)
			scanner.clear()
			sleep(self.delay)
