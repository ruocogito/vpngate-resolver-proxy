#!/bin/sh
echo "Provisioning tun device"                                                                                          mkdir -p /dev/net
mkdir -p /dev/net
rm /data/danted.log
if [ ! -c /dev/net/tun ]; then
	mknod /dev/net/tun c 10 200
fi

sleep 2

#danted -D -f /etc/danted.conf

#add route for local network

# Get the default gateway
DEFAULT_GATEWAY=$(ip route show default | awk '/default/ {print $3}')

# Check if the default gateway was found
if [ -z "$DEFAULT_GATEWAY" ]; then
  echo "Error: Default gateway not found."
  exit 1
fi

# Check if the SUBNET environment variable is set
if [ -z "$SUBNET" ]; then
  echo "Error: SUBNET environment variable is not set."
  exit 1
fi

# Add the route
echo "Adding route for $SUBNET via $DEFAULT_GATEWAY..."
ip route add $SUBNET via $DEFAULT_GATEWAY

# Verify the route was added
if ip route | grep -q "$SUBNET"; then
  echo "Route added successfully:"
  ip route | grep "$SUBNET"
else
  echo "Error: Failed to add route for $SUBNET."
  exit 1
fi

python3 /usr/src/app/index.py > /data/python3.log 2>&1
