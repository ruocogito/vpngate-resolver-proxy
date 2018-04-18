# VPNGate Auto Setup Script for OpenVPN on Linux

[VPNGate](http://vpngate.net) is a an excellent VPN for beginners. But one of the problems is that older ovpn connections stop connecting after a few days. I can easily add them manually, but downloading the ovpn files and adding them every week is a mess! This script easily adds up to date 4 connections from VPNGate records.

## Requirements
- Only supports Linux
- Requires `network-manager-openvpn` & `network-manager-openvpn-gnome` to be installed
- __Python 3__ (Python 2 not tested)

## Instructions
Just download and run:
```
python3 autovpngate.py
```

It will take some time (it will download ~2MB file of records for latest connections) and it will ask for sudo password. Provide the password. Now you should have some connections on your NetworkManager, like `vpngateauto_1_JP`, `vpngateauto_2_HK` etc.

_Previously you had to delete all the previous auto connections in Network Manager. Now it automatically does it for you. So just run and connect!_

--- You are welcome to improve it! ---

Have fun!