#! /usr/bin/env python
# License: CC0
# From: https://gist.github.com/adnan360/f5bf854a9278612e0effedbfa202d6fc
# Run: python3 autovpngate.py

# For CSV parsing and ovpn file handling
import os
import csv
import base64, string
import subprocess
from subprocess import Popen, PIPE
# For regex
import re

try:
	# For Python 3.0 and later
	from urllib.request import urlopen
except ImportError:
	# Fall back to Python 2's urllib2
	from urllib2 import urlopen

storagepath = '/tmp/'

# --------------- Functions ---------------

def runme(program):
	p = subprocess.Popen([program], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output = ''
	for line in p.stdout.readlines():
		#print(line)
		output = output+'\n'+line.decode("utf-8")
	retval = p.wait()
	return output

def deletefile(filename):
	if os.path.isfile(filename):
		os.remove(filename)


# --------------- Get data from vpngate ---------------

print('downloading latest vpn connection data...')
data = urlopen("http://www.vpngate.net/api/iphone/")
print('download finished...')
print('processing...')
htmlcode = data.read().decode('UTF-8')

deletefile(storagepath+'output.csv')
f = open(storagepath+'output.csv', 'w')
f.write(htmlcode)


# --------------- Handle CSV and OVPN ---------------

print('updating connections...')
with open(storagepath+'output.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	count = 0

	# find previous auto connections
	output = runme('sudo /usr/bin/nmcli connection show')
	connections = [word for word in output.split() if word.startswith('vpngateauto')]
	# remove previous auto connections
	for conn in connections:
		print('deleting previously created auto connection '+conn+'...')
		runme('sudo /usr/bin/nmcli connection delete id '+conn)

	for row in reader:
		# take first 6 connections
		if count < 6:
			if len(row) > 13 and row[14] != 'OpenVPN_ConfigData_Base64':
				count = count + 1
				decoded = base64.b64decode(row[14])
				countrycode = row[6]
				ovpnname = 'vpngateauto_'+str(count)+'_'+countrycode
				deletefile(storagepath+ovpnname+'.ovpn')
				with open(storagepath+ovpnname+'.ovpn', 'a') as out:
					out.write(decoded.decode('UTF-8') + '\n')
				# create connection
				print('creating vpngate auto connection '+ovpnname+'...')
				runme('sudo /usr/bin/nmcli connection import type openvpn file '+storagepath+ovpnname+'.ovpn')
				deletefile(storagepath+ovpnname+'.ovpn')
				deletefile(storagepath+'output.csv')
		else:
			break
