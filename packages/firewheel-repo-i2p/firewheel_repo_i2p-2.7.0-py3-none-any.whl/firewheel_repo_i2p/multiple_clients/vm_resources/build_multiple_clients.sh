#!/bin/bash

GW=$(ip route | grep default | awk '{print $3}')
IP_PREFIX=$(ip addr show dev br0 | grep 'global br0' | awk '{print $2}' | awk -F\. '{print $1 "." $2}')
SUBNET=$(ip addr show dev br0 | grep 'global br0' | awk '{print $2}' | cut -d'/' -f2)
if [ $SUBNET -gt 16 ]; then echo "ERROR: very small subnet."; exit 1; fi

NUM_CLIENTS=$1

cat /home/ubuntu/.i2p/router.config | grep -v Pool | grep -v pdate |
            grep -v password | grep -v Version | grep -v i2np.udp |
            grep -v first > /tmp/i2p-config-part
cp /home/ubuntu/.i2p/i2psnark.config.d/i2psnark.config /tmp/i2ps

cat >/multi-client.sh <<EOF
#!/bin/bash
sleep 600
python /var/launch/600/add_tracktor_address.py/add_tracktor_address.py
python /multi-client-snark.py
EOF
chmod +x /multi-client.sh
cat >/multi-client-snark.py <<EOF
#!/usr/bin/env python
import sys
import urllib
import urllib2
import json
import os
import os.path
import subprocess
import random
import socket
import hashlib
import time

class SubscribeTorrent(object):

    def run(self):
        torrent_list_url = 'http://superhidden-bttrack.internet.net:9998/torrentlist'

        # Get list of torrents
        torrent_names = self.get_torrent_list(torrent_list_url)
        if len(torrent_names) == 0:
            return

        # Pick a torrent to get
        torrent_url = self.pick_torrent(torrent_names)

        # Load url into i2psnark
        self.request_torrent(torrent_url)

        # Start everything
        while True:
            self.start_torrents()
            time.sleep(600)

    def start_torrents(self):
        content = urllib2.urlopen('http://127.0.0.1:7657/i2psnark/')
        ret = content.read()

        for l in ret.split('\n'):
            if 'nonce' in l:
                n = l.split()[3].split('"')[1]
                try:
                    int(n[:5])
                    nonce=n
                except:
                    continue
        data = "nonce=%s&action_StartAll.x=2&action_StartAll.y=2" % (nonce)
        content = urllib2.urlopen('http://127.0.0.1:7657/i2psnark/?%s' % data)

    def get_torrent_list(self, torrent_list_url):
        try:
            content = urllib2.urlopen(torrent_list_url)
            ret = content.read()
            torrent_list = []
            for t in ret.split('\n'):
                # find link
                torrent_list.append(t)

            return torrent_list
        except:
            return []

    def request_torrent(self, torrent_url, file_location=''):
        content = urllib2.urlopen('http://127.0.0.1:7657/i2psnark/')
        ret = content.read()

        for l in ret.split('\n'):
            if 'nonce' in l:
                n = l.split()[3].split('"')[1]
                try:
                    int(n[:5])
                    nonce=n
                except:
                    continue

        data = "nonce=%s&action=Add&nofilter_newURL=%s&foo=Add+torrent&nofilter_newDir=" % (nonce, urllib.quote(torrent_url))
        content = urllib2.urlopen('http://127.0.0.1:7657/i2psnark/?%s' % data)

    def pick_torrent(self, torrent_names):
        # We want to bias towards 'popular' torrents, but with some reasonable probability pick any torrent
        # We want to sample with replacement, so if we already chose it then we will just wait for the next pick
        t = {}
        for torrent_name in torrent_names:
            h = hashlib.sha256()
            h.update(torrent_name)
            t[h.digest()] = torrent_name

        sorted_t = sorted(t.keys())
        max_val = len(sorted_t)

        # Use some distribution, here we choose beta
        pos = int(max_val*random.betavariate(2,5))

        return t[sorted_t[pos]]

if __name__ == '__main__':
    st = SubscribeTorrent()
    st.run()
EOF
chmod +x /multi-client-snark.py

# Setup the given number of i2p routers
for N in $(seq 1 $NUM_CLIENTS); do
    user="u-i2p$N"
    userc="sudo -u $user -i"
    ns="ns-i2p$N"
    vi="in-i2p$N"
    vo="out-i2p$N"
    nse="ip netns exec $ns"
    ip="$IP_PREFIX.$((N/254+5)).$((N%254))/$SUBNET"

    # Create the IP namespace
    ip netns add $ns
    $nse ip link set lo up

    # Create the veth into/outof the namespace
    ip link add $vo type veth peer name $vi
    ip link set $vi netns $ns
    ip link set $vo up
    $nse ip link set $vi up
    brctl addif br0 $vo

    # Set the IP address / gateway inside the namespace
    $nse ip addr add dev $vi $ip
    $nse ip route add default via $GW

    # Create the I2P user
    useradd -m $user

    # Start I2P for the user in the namespace
    $nse $userc i2prouter start

    # Wait for the netDb to create a router entry
    pushd /home/$user

    until ls .i2p/netDb; do echo "Waiting for i2p dir..."; sleep 1; done

    pushd .i2p/netDb

    i=0
    until find -name '*.dat' | grep dat; do
        echo "Waiting for .dat file..."; sleep 5;
        ((i++))
        if [ "$i" -eq 5 ]; then
            echo "After waiting a brutal 25 sec, killing and restarting i2p"
            $nse $userc i2prouter restart
            echo "Restarted, waiting 5 sec for .dat file"
            sleep 5
            i=0
        fi
    done

    popd

    $nse $userc i2prouter stop

    # Set the config entries to match the host
    cat /tmp/i2p-config-part >> /home/$user/.i2p/router.config
    cat /tmp/i2ps >> /home/$user/.i2p/i2psnark.config.d/i2psnark.config

    # Copy up the router configuration
    cp -r /home/$user/.i2p/netDb /tmp/netDb
    chown ubuntu:ubuntu -R /tmp/netDb
    until sudo -u ubuntu -H scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -oConnectTimeout=5 -r /tmp/netDb i2pbootstrap.internet.net: ; do echo "Waiting for scp..."; sleep 5; done
    rm -rf /tmp/netDb

done
