from flask import Flask, render_template
from btscan import BTScan
from os import environ
from datetime import datetime
import requests

alertHttpUrl = environ['ALERT_HTTP']
notifyHttpUrl = environ['NOTIFY_HTTP']
alertTimer = int(environ['ALERT_TIMER'])
notifyTimer = int(environ['NOTIFY_TIMER'])

proximityAddress = environ['BLE_PROXIMITY_ADDRESS']
scanDelay = int(environ['BLE_SCAN_DELAY'])
scanTimeout = int(environ['BLE_SCAN_TIMEOUT'])
proximityMax = int(environ['PROXIMITY_MAX'])
proximityThreshold = int(environ['PROXIMITY_THRESHOLD'])

addresses = None if proximityAddress == None else [ proximityAddress ]
neighbors = []
proximityEnterTimes = {}
lastNotifyTimes = {}

def sendNotify(addr):
	r = requests.get(notifyHttpUrl)
	if r.status_code == 200:
		print('SENT NOTIFICATION')
	else:
		print('Error on notify http request:', r)

def sendAlert(addr):
	r = requests.get(alertHttpUrl)
	if r.status_code == 200:
		print('SENT ALERT')
	else:
		print('Error on alert http request:', r)

def updateNotify(addr, duration):
	lastNotify = lastNotifyTimes.get(addr, None) 
	time = duration if lastNotify == None else datetime.now() - lastNotify

	if time.total_seconds() > notifyTimer:
		sendNotify(addr)
		lastNotifyTimes[addr] = datetime.now()

def updateAlert(addr, duration):
	if duration.total_seconds() > alertTimer:
		sendAlert(addr)

		# clear the times, so they can reset
		proximityEnterTimes[addr] = None
		lastNotifyTimes[addr] = None

def onScan(newNeighbors):
	neighbors = newNeighbors

	for neighbor in neighbors:
		duration = updateProximityTime(neighbor.addr, neighbor.rssi)
		print('Scan:', neighbor.addr, neighbor.localName, neighbor.rssi, duration)

		if duration != None:
			updateNotify(neighbor.addr, duration)
			updateAlert(neighbor.addr, duration)

def updateProximityTime(addr, rssi):
	enterTime = proximityEnterTimes.get(addr)

	if enterTime == None:
		# this device previously was not in the area
		if rssi >= proximityThreshold:
			# this device has entered the area
			proximityEnterTimes[addr] = datetime.now()
		else:
			# this device has not yet entered the area
			proximityEnterTimes[addr] = None
			lastNotifyTimes[addr] = None
		return None
	else:
		# this device previously was in the area
		if rssi >= proximityMax:
			# this device is still in the area
			return datetime.now() - enterTime
		else:
			# this device has left the area
			proximityEnterTimes[addr] = None
			lastNotifyTimes[addr] = None


btScan = BTScan(addresses=addresses, onScan=onScan, timeout=scanTimeout, delay=scanDelay)
btScan.start()

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html', proximityAddress=proximityAddress, neighbors=neighbors)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
