#! /usr/bin/env python
# License: CC0
# From: https://gist.github.com/adnan360/f5bf854a9278612e0effedbfa202d6fc
# Run: python autovpngate.py

import base64
import csv
# For CSV parsing and ovpn file handling
import os
import re
import shutil
import string
import subprocess
import sys
import time
import urllib.request
from subprocess import Popen, PIPE
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
import json
import speedtest

#storagepath = 't:/'
storagepath = '/data/'
output_file = 'output.csv'
backup_file = 'backup_vpnlist.csv'
log_file = 'log.txt'
url_test_file = 'urltest.txt'
config_name = 'vpn-resolver.conf'
vpnlist_last_update_sec = 0

# --------------- Functions ---------------

def writelog(logmsg):
    with open(storagepath + log_file, 'a') as logfile:
        logfile.write('%s\n' % logmsg)


class RunMe:
    def __init__(self, command):
        self.command = command

    def __enter__(self):
        # Execute the command and capture output
        import subprocess
        self.process = subprocess.Popen([self.command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout, self.stderr = self.process.communicate()
        return self.stdout.decode('utf-8')

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up resources if needed
        pass


def runme(program):
    p = subprocess.Popen([program], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    for line in p.stdout.readlines():
        # print(line)
        output = output + '\n' + line.decode("utf-8")
    retval = p.wait()
    return output


class Configuration:
    def __init__(self):
        file_path = f'{config_name}'
        # Default configuration values
        self.country_codes = []
        self.min_download_speed = 0.0
        self.min_wait_seconds = 0.0
        self.url_timeout_seconds = 0.0
        self.vpnlist_update_period_seconds = 0.0
        self.think_interval_seconds = 0.0
        self.ignore_speed_test = False
        self.ignore_urls_test = False

        # Read and parse the configuration file
        self._read_configuration(file_path)

    def _read_configuration(self, file_path):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    # Skip comments and empty lines
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Split the line into key and value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Parse the key-value pairs
                        if key == 'country_codes':
                            # Split the value by commas and strip whitespace
                            self.country_codes = [code.strip().capitalize() for code in value.split(',')]
                        elif key == 'min_download_speed':
                            # Convert to float (supports both int and double)
                            self.min_download_speed = float(value)
                        elif key == 'min_wait_seconds':
                            # Convert to float (supports both int and double)
                            self.min_wait_seconds = float(value)
                        elif key == 'url_timeout_seconds':
                            self.url_timeout_seconds = float(value)
                        elif key == 'vpnlist_update_period_seconds':
                            self.vpnlist_update_period_seconds = float(value)
                        elif key == 'think_interval_seconds':
                            self.think_interval_seconds = float(value)
                        elif key == 'ignore_speed_test':
                            self.ignore_speed_test = bool(value)
                        elif key == 'ignore_urls_test':
                            self.ignore_urls_test = bool(value)
                        else:
                            writelog(f"Warning: Unknown key '{key}' in configuration file.")
        except FileNotFoundError:
            writelog(f"Error: Configuration file '{file_path}' not found.")
        except ValueError as e:
            writelog(f"Error: Invalid value in configuration file: {e}")
        except Exception as e:
            writelog(f"Error: An unexpected error occurred: {e}")

    def __repr__(self):
        return (f"Configuration(country_codes={self.country_codes}, "
                f"min_download_speed={self.min_download_speed}, "
                f"min_wait_seconds={self.min_wait_seconds})")


config = Configuration()


def deletefile(relative_filename):
    if os.path.isfile(storagepath + relative_filename):
        os.remove(storagepath + relative_filename)


def isVpnListConsistent(relative_filename):
    try:
        if not os.path.isfile(storagepath + relative_filename):
            return False
        with open(storagepath + relative_filename, 'r') as file:
            lines = file.readlines()

            # Check if file is not empty and contains specific substrings
            if len(lines) == 0:
                return False
            if not any("vpn_servers" in line for line in lines):
                return False
            if "#HostName," not in lines[1]:
                return False

        return True
    except Exception as e:
        writelog(f"An error occurred while checking the file: {e}")
        return False


def getDataFromVpnGate():
    global vpnlist_last_update_sec
    try:
        if int(time.time()) - vpnlist_last_update_sec <= config.vpnlist_update_period_seconds:
            return
        writelog('downloading latest vpn connection data...')
        data = urlopen("http://www.vpngate.net/api/iphone/", timeout=config.url_timeout_seconds)
        htmlcode = data.read()

        deletefile(output_file)
        f = open(storagepath + output_file, 'wb')
        f.write(htmlcode)

        deletefile(backup_file)
        shutil.copy(storagepath + output_file, storagepath + backup_file)

        vpnlist_last_update_sec = int(time.time())

        writelog(f'download finished...creating {backup_file}')
    except (URLError, HTTPError) as e:
        writelog(f"Failed to download data: {e}")
    except Exception as e:
        writelog(f"An error occurred: {e}")


# ----------- is any vpn list is consistent -------------
def prepareVpnList():
    if not isVpnListConsistent(output_file):
        if os.path.exists(storagepath + backup_file) and isVpnListConsistent(backup_file):
            # Copy output.csv with backup_vpnlist.csv
            deletefile(output_file)
            shutil.copy(storagepath + backup_file, storagepath + output_file)
            writelog(f"{backup_file} has been used against of {output_file}")
        else:
            writelog(f"Both {output_file} and {backup_file} are not consistent. Terminating program.")
            exit(1)
    else:
        writelog(f"{output_file} is consistent.")


def getVpnListFromFile():
    with open(storagepath + output_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        vpnList = [row for row in reader]
    vpnList = list(
        filter(
            lambda x: not (['*'] == x or '*vpn_servers' in x or '#HostName' in x or int(x[7]) == 0) and len(x) > 13 and
                      x[6].capitalize() in config.country_codes, vpnList)
    )
    vpnList.sort(key=lambda x: float(int(x[4])) / float(x[7]), reverse=True)
    return vpnList


def isTunUp():
    with RunMe('ip a show tun0') as consoleOut:
        return 'tun0:' in consoleOut and 'inet' in consoleOut


def getSpeed(atempt_num=0):
    if atempt_num > 3:
        return
    try:
        st = speedtest.Speedtest(secure=True)
        st.get_servers()
        if atempt_num == 0:
            st.get_best_server()
        else:
            st.get_closest_servers()

        download_speed = st.download() / 1_000_000  # Convert to Mbps
        # upload_speed = st.upload() / 1_000_000      # Convert to Mbps

        writelog(f"Download Speed: {download_speed:.2f} Mbps")
        # writelog(f"Upload Speed: {upload_speed:.2f} Mbps")
    except Exception as e:
        writelog("Failed run speedtest")
        return -1
    return download_speed


def check_page_load_time(url, substring):
    try:
        with open("headers.json", "r") as file:
            headers = json.load(file)

        # Start the timer
        start_time = time.time()

        # Create a Request object with the URL and headers
        request = urllib.request.Request(url, headers=headers)

        # Send the request and read the response
        with urllib.request.urlopen(request) as response:
            page_content = response.read().decode('utf-8')  # Decode bytes to string

        # Stop the timer
        end_time = time.time()
        load_time_ms = (end_time - start_time)

        if len(substring) > 0 and not substring in page_content:
            print(f"Failed check_page_load_time: substring not in page_content")
            return -1

        writelog(f'{url} has success loaded at {load_time_ms:.4f}')
        return load_time_ms

    except Exception as e:
        print(f"Error in check_page_load_time {url}: {e}")
        return -1


def read_url_test_file():
    # Initialize empty lists for the first and second words
    urls = []
    urls_substrs = []

    # Open the file and read line by line
    with open(f'{url_test_file}', 'r') as file:
        for line in file:
            # Skip lines that start with '#'
            if line.startswith('#'):
                continue

            # Split the line by ',' and strip whitespace from each word
            parts = [part.strip() for part in line.split(',')]

            # Handle cases where there is only one word in the row
            if len(parts) == 1:
                urls.append(parts[0])
                urls_substrs.append('')  # Add empty string for the second word
            elif len(parts) == 2:
                urls.append(parts[0])
                urls_substrs.append(parts[1])
            # Ignore rows with more than two words (optional, based on requirements)

    # Return the result as an object (dictionary in Python)
    return {
        'urls': urls,
        'urls_substrs': urls_substrs
    }

def sgn(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def isConnectConsistent():
    att1 =  config.ignore_speed_test and getSpeed() > config.min_download_speed or True

    urls_test = read_url_test_file()
    att2 = config.ignore_urls_test and sum(list(
        map(lambda pair: sgn(check_page_load_time(pair[1], urls_test["urls_substrs"][pair[0]])),
            enumerate(urls_test["urls"]))
    )) == len(urls_test["urls"]) or True
    return att1 and att2

def start_dante_if_not_running():
    with RunMe("ps aux | grep danted | grep -v grep") as ps_out:
        if not 'danted' in ps_out:
            writelog('Detected that danted not running, launch it')
            runme('danted -D -f /etc/danted.conf')

def connectingWhileFailed(vpnList):
    for index, row in enumerate(vpnList):
        # take first N connections
        decoded = base64.b64decode(row[14])
        countrycode = row[6]
        ovpnname = 'vpn_' + str(index) + '_' + countrycode
        deletefile(ovpnname + '.ovpn')
        with open(storagepath + ovpnname + '.ovpn', 'a') as out:
            out.write(decoded.decode('UTF-8') + '\n')
        # create connection
        writelog('creating vpngate connection ' + ovpnname + '...')
        runme(f'openvpn --config {storagepath + ovpnname}.ovpn --daemon --log {storagepath}openvpn.log')
        time.sleep(config.min_wait_seconds)

        if isTunUp():
            writelog(f'{ovpnname} connected success')
            if not isConnectConsistent():
                writelog("connection is not consistent, stop it")
            else:
                writelog("connection is consistent")
                start_dante_if_not_running()
                break
        writelog(f'{ovpnname} connection failed: timeout 7 sec')
        runme('pkill openvpn')
        time.sleep(1)
        deletefile(ovpnname + '.ovpn')
        # writelog(runme('/usr/bin/nmcli connection import type openvpn file ' + storagepath + ovpnname + '.ovpn'))
        # deletefile(ovpnname+'.ovpn')
        # deletefile(output_file)


# find previous auto connections
# output = runme('/usr/bin/nmcli connection show')
# connections = [word for word in output.split() if word.startswith('vpn_')]
# remove previous auto connections
# for conn in connections:
#    writelog('deleting previously created auto connection '+conn+'...')
#    runme('/usr/bin/nmcli connection delete id '+conn)

try:
    deletefile(log_file)
    deletefile(output_file)
    deletefile('openvpn.log')
    runme(f'rm -v {storagepath}*.ovpn')

    #isConnectConsistent()
    while True:
        getDataFromVpnGate()
        if not isTunUp():
            prepareVpnList()
            vpnList = getVpnListFromFile()
            connectingWhileFailed(vpnList)
        time.sleep(config.think_interval_seconds)
except Exception as e:
    print(f"Script was terminated abnormaly: {e}")
