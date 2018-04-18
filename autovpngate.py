#! /usr/bin/env python
# License: CC0

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

data = urlopen("http://www.vpngate.net/api/iphone/")
htmlcode = data.read().decode('UTF-8')

deletefile('output.csv')
f = open('output.csv', 'w')
f.write(htmlcode)


# --------------- Handle CSV and OVPN ---------------

with open('output.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	count = 0

	# delete previous auto connections
	output = runme('sudo /usr/bin/nmcli connection show')
	#print( 'output:'+output )
	connections = [word for word in output.split() if word.startswith('vpngateauto')]
	# remove connection
	for conn in connections:
		print('deleting previously created auto connection '+conn+'...')
		runme('sudo /usr/bin/nmcli connection delete id '+conn)

	for row in reader:
		# take first 4 connections
		if count < 4:
			if len(row) > 13 and row[14] != 'OpenVPN_ConfigData_Base64':
				count = count + 1
				decoded = base64.b64decode(row[14])
				countrycode = row[6]
				ovpnname = 'vpngateauto_'+str(count)+'_'+countrycode
				deletefile(ovpnname+'.ovpn')
				with open(ovpnname+'.ovpn', 'a') as out:
					out.write(decoded.decode('UTF-8') + '\n')
				# create connection
				print('creating vpngate auto connection '+ovpnname+'...')
				runme('sudo /usr/bin/nmcli connection import type openvpn file '+ovpnname+'.ovpn')
				deletefile(ovpnname+'.ovpn')
				deletefile('output.csv')
		else:
			break
