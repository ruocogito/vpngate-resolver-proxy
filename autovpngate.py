#! /usr/bin/env python


# For CSV parsing and ovpn file handling
import os
import csv
import base64, string
import subprocess
from subprocess import Popen, PIPE

try:
	# For Python 3.0 and later
	from urllib.request import urlopen
except ImportError:
	# Fall back to Python 2's urllib2
	from urllib2 import urlopen


# --------------- Functions ---------------

def runme(program):
	p = subprocess.Popen([program], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print(line)
	retval = p.wait()

def deletefile(filename):
	if os.path.isfile(filename):
		os.remove(filename)


# --------------- Get data from vpngate ---------------

data = urlopen("http://www.vpngate.net/api/iphone/")
htmlcode = data.read().decode('UTF-8')

deletefile('output.csv')
f = open('output.csv', 'w')
f.write(htmlcode)


# --------------- Handle CSV and OVPN ---------------

with open('output.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	count = 0
	for row in reader:
		# take first 2 connections
		if count < 2:
			if len(row) > 13 and row[14] != 'OpenVPN_ConfigData_Base64':
				count = count + 1
				decoded = base64.b64decode(row[14])
				countrycode = row[6]
				deletefile('vpngateauto_'+countrycode+'_'+str(count)+'.ovpn')
				with open('vpngateauto_'+countrycode+'_'+str(count)+'.ovpn', 'a') as out:
					out.write(decoded.decode('UTF-8') + '\n')
				# remove connection
				runme('sudo /usr/bin/nmcli connection delete id vpngateauto_'+countrycode+'_'+str(count))
				# create connection
				runme('sudo /usr/bin/nmcli connection import type openvpn file vpngateauto_'+countrycode+'_'+str(count)+'.ovpn')
				deletefile('vpngateauto_'+countrycode+'_'+str(count)+'.ovpn')
				deletefile('output.csv')
		else:
			break
