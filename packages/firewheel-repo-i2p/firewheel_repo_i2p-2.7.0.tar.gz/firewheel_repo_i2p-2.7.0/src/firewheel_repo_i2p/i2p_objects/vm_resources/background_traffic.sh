#!/bin/bash

# Get the I2P address to fetch from.
until grep b32 /tmp/traffic_address; do
    wget -O /tmp/traffic_address cc.internet.net:9999/address
    sleep 30
done

# Set our HTTP proxy so we use I2P
export http_proxy=127.0.0.1:4444

# Repeat forever:
while [ 1 ]
do
    # Download the large file.
    wget --timeout=20 -O/dev/null $(cat /tmp/traffic_address)/small.bin
    # Wait
    sleep 60
done
