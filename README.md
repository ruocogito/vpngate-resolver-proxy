# vpngate-resolver-proxy
A Docker container with OpenVPN automatically establishes a working VPNGate connection and opens a local proxy.


## Prerequisites

To run this project, you need the following installed on your system:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Compatibility

This project has been tested and is confirmed to work on **Linux**. It may not be compatible with other operating systems.

## Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/ruocogito/vpngate-resolver-proxy.git
   ``` 
2. Copy .env.example to .env
   Add your local subnet (the subnet of your working PC and Docker host machine) with the mask to the SUBNET variable.
3. Start the container:
   ```bash
   docker compose up 
   ```
4. Wait while the script finds a useful VPNGate VPN.
   You will see "connection is consistent" at the end of data/out.txt.

## Configurations

- vpn-resolver.conf
  Configuration file for the auto-setup script.
- dante.conf
  Configuration file for the Dante proxy server.
- urltest.txt
  File containing URLs that must be accessed through the VPN and substrings that must be present in the page code.

##Logs
- /data/log.txt
  Log file for the auto-setup script. You can see messages about updating the VPN list and checking VPN URLs.
- /data/openvpn.log
  Log file for OpenVPN.
- /data/danted.log
  Log file for the Dante proxy server.
- /data/python3.log
  Log file for the Python3 auto-setup script.
- /data/*.csv
  Files containing the VPN list downloaded from the VPNGate server. *Do not delete these files manually!*
- /data/*.ovpn
  Files containing OpenVPN connection configurations. These are dynamically created when the VPN connection is reestablished.

## What it does?

1. Retrieves a list of public VPNGate VPNs from `backup_vpnlist.csv` or downloads a new list to `output.csv`.
2. Builds a list of VPN entities ordered by **[Speed/NumVpnSessions]** in descending order, excluding VPNs with zero `NumVpnSessions`.
3. If no VPN is connected (no `tun0` interface), it connects to the VPN at the top of the list.
4. If the VPN speed is lower than the configured threshold or the URLs from `urltest.txt` are inaccessible, it shuts down the VPN and tries the next VPN in the list.

**Note**: The VPN list in `backup_vpnlist.csv` may become outdated. If the VPNGate page is blocked by your provider, the app cannot update it automatically.

You can manually update `backup_vpnlist.csv` by:
1. Opening the [VPN list](http://www.vpngate.net/api/iphone/) page.
2. Copying the text information and saving it to `backup_vpnlist.csv`.

#THANKS
- https://github.com/adnan360 for VPNGate Auto Setup Script for OpenVPN on Linux
=======
# VPNGate Auto Setup Script for OpenVPN on Linux

[VPNGate](http://vpngate.net) is a an excellent VPN for beginners. But one of the problems is that older ovpn connections stop connecting after a few days. I can easily add them manually, but downloading the ovpn files and adding them every week is a mess! This script easily adds up to date 6 connections from VPNGate records.

--- You are welcome to improve it! ---

Have fun!
