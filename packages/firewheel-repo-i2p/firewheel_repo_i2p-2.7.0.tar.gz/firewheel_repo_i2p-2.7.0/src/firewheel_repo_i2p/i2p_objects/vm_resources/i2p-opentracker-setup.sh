#!/bin/bash

cat >/etc/init/i2popentracker.conf <<EOF
description "i2popentracker"

start on filesystem or runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5
umask 022

script
    /usr/bin/i2p-opentracker
end script
EOF
ln -s /lib/init/upstart-job /etc/init.d/i2popentracker

service i2popentracker start


# Next, wait until we get our tunnel local destination to share
mkdir -p /srv/torrents
chmod 1777 /srv/torrents
sudo chmod 1777 /srv

cat >/etc/init/websrv.conf <<EOF
description "websrv"

start on filesystem or runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5
umask 022

script
    chdir /srv
    busybox httpd -f -p 9998
end script
EOF
ln -s /lib/init/upstart-job /etc/init.d/websrv

service websrv start

tunnum="ne"
until  [[ $tunnum == *"tunnel"* ]]; do
    if [[ $tunnum != "ne" ]]; then
        sleep 60
    fi
    tunnum=$(wget --timeout=30 -O- http://127.0.0.1:7657/i2ptunnel | grep tracktor | cut -d'"' -f4)
done

# Now, get the base64 address
ld="ne"
until [[ $ld == *"Read Only: Local Destination"* ]]; do
    if [[ $ld != "ne" ]]; then
        sleep 20
    fi
    ld=$(wget --timeout=30 -O- http://127.0.0.1:7657/i2ptunnel/$tunnum | grep "Read Only: Local Destination")
done
b64a=$(echo $ld | sed 's/</>/g' | cut -d'>' -f3)

echo $b64a > /srv/tracktor.i2p
sudo chmod 1777 /srv/tracktor.i2p

# Now, continue to build the torrent lists
while [ 1 ]; do
    find /srv/torrents -type f -exec grep php '{}' \; > /srv/list.new
    mv /srv/list.new /srv/torrentlist
    sleep 30
done
