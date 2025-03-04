#!/bin/bash

pushd /home/ubuntu

pushd .i2p

# Grab the netDb
until sudo -u ubuntu -H tar xf netdb.tgz; do
    st=$((RANDOM%30));
    echo "Waiting to grab netdb... ($st)"
    sleep $st;
    sudo -u ubuntu -H wget --timeout=20 -O netdb.tgz http://i2pbootstrap.internet.net:9998/netdb.tgz
done

popd

# Start I2P
sudo -u ubuntu -H i2prouter start

popd

until netstat -tlpn | grep 7657; do
    st=$((RANDOM%10));
    echo "waiting for port ... ($st)"
    sleep $st
done
echo "done"

mkdir /tmp/get-netdb-finished
