#!/bin/bash

# Host a web server on port 9999 with a file 'large.bin'
/bin/mkdir -p /srv
/bin/dd if=/dev/urandom of=/srv/large.bin bs=1M count=10
/bin/dd if=/dev/urandom of=/srv/small.bin bs=512 count=1

cat >/etc/init/c0ers10n.conf <<EOF
description "c0ers10n"

start on filesystem or runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5
umask 022

script
    chdir /srv
    busybox httpd -f -p 9999
end script
EOF
ln -s /lib/init/upstart-job /etc/init.d/c0ers10n

service c0ers10n start
