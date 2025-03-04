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
tunid="ne"
until  [[ $tunid == *"b32.i2p"* ]]; do
    if [[ $tunid != "ne" ]]; then
        sleep 60
    fi
    tunid=$(wget --timeout=30 -O- http://127.0.0.1:7657/i2ptunnel | grep -A10 mytrack | tail -1 | cut -d'"' -f6)
done

echo $tunid > /mytrack.i2p
chmod 0644 /mytrack.i2p

cat >/usr/local/bin/add-mytrack <<EOF
#!/usr/bin/env python

import mechanize

def main():

    # Try to get the base64 address
    b32 = ''
    with open('/mytrack.i2p') as f:
        b32 = f.readline().strip()

    br = mechanize.Browser()
    br.open('http://127.0.0.1:7657/i2psnark/configure')

    br.select_form(nr=1)
    br['tname'] = 'mytrack'
    br['thurl'] = b32
    br['taurl'] = b32 + '/announce.php'

    br.submit(name='taction', label='Add tracker')

if __name__ == '__main__':
    main()
EOF
chmod 0755 /usr/local/bin/add-mytrack
/usr/local/bin/add-mytrack
