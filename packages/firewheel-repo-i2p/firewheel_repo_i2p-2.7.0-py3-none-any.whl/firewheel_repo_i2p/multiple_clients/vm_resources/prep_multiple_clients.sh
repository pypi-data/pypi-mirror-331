#!/bin/bash

NIC=$(ls /proc/sys/net/ipv4/conf | grep eth)
ifdown $NIC
cat > /etc/network/interfaces <<EOF
auto lo
iface lo inet loopback
auto $NIC
iface $NIC inet manual
auto br0
iface br0 inet static
bridge_ports $NIC
EOF
cat /etc/network/interfaces.d/* | tail -n 4 >> /etc/network/interfaces

ifup br0

swapoff -a
