<<<<<<< HEAD
# vpngate-resolver-proxy
Docker container with openvpn itself resolve working vpngate connection and open local proxy
=======
# VPNGate Auto Setup Script for OpenVPN on Linux

[VPNGate](http://vpngate.net) is a an excellent VPN for beginners. But one of the problems is that older ovpn connections stop connecting after a few days. I can easily add them manually, but downloading the ovpn files and adding them every week is a mess! This script easily adds up to date 6 connections from VPNGate records.

## Requirements
- Only supports Linux
- Requires `network-manager-openvpn` & `network-manager-openvpn-gnome` to be installed
- Python 2 or 3

## Instructions
Just download and run:
```
sudo python autovpngate.py
```

It will take some time (it will download ~2MB file of records for latest connections) and it will ask for sudo password. Provide the password. Now you should have some connections on your NetworkManager, like `vpngateauto_1_JP`, `vpngateauto_2_HK` etc. Some connections may not work. So you can try the first one, if it doesn't work go on to the next one, etc.

It does basically 3 things:

- Downloads the latest vpn connection data
- Deletes previously create auto vpn connections (if any)
- Creates auto vpn connections


Example output:

```
$> sudo python autovpngate.py
downloading latest vpn connection data...
download finished...
processing...
updating connections...
deleting previously created auto connection vpngateauto_1_JP...
deleting previously created auto connection vpngateauto_2_JP...
deleting previously created auto connection vpngateauto_3_JP...
deleting previously created auto connection vpngateauto_4_KR...
deleting previously created auto connection vpngateauto_5_PE...
deleting previously created auto connection vpngateauto_6_PE...
creating vpngate auto connection vpngateauto_1_JP...
creating vpngate auto connection vpngateauto_2_JP...
creating vpngate auto connection vpngateauto_3_JP...
creating vpngate auto connection vpngateauto_4_KR...
creating vpngate auto connection vpngateauto_5_PE...
creating vpngate auto connection vpngateauto_6_PE...
```


_Previously you had to delete all the previous auto connections in Network Manager. Now it automatically does it for you. So just run and connect!_

--- You are welcome to improve it! ---

Have fun!
>>>>>>> master
