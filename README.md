# VPNGate Auto Setup Script for OpenVPN on Linux

[VPNGate](http://vpngate.net) is a an excellent VPN for beginners. But one of the problems is that older ovpn connections stop connecting after a few days. I can easily add them manually, but downloading the ovpn files and adding them every week is a mess! This script easily adds up to date 2 connections from VPNGate records.

## Requirements
- Only supports Linux
- `networkmanager-openvpn`
- __Python 3__ (Python 2 not tested)

## Instructions
Just download and run:
```
python3 autovpngate.py
```

It will take some time (it will download ~2MB file of records for latest connections) and it will ask for password. Provide the password. Now you should have some connections on your NetworkManager, like `vpngateauto_JP_1`, `vpngateauto_HK_2` etc.

_If you run this second time, don't forget to delete the `vpngateauto_xyz` connections from Network Manager._

--- You are welcome to improve it! ---

Have fun!