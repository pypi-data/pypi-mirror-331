#!/bin/bash

# 0) assume tunnel setup
# 1) setup cgi-bin script
cat >/home/ubuntu/.i2p/eepsite/cgi-bin/upload.cgi <<EOF
#!/usr/bin/env python

# Example from:
# stackoverflow.com/questions/4890820/how-to-use-python-cgi-for-file-uploading

import cgi, os
import cgitb; cgitb.enable()
import sys

print 'Content-Type: text/html\n'

form = cgi.FieldStorage()
upload = form['file']

print 'Lolz security. This is I2P. We don\'t need security.<br><br>'

name = os.path.basename(upload.filename)
print 'Saving: %s<br>' % name

with open('/home/ubuntu/.i2p/eepsite/docroot/torrents/%s' % name, 'wb') as of:
    while True:
        buf = upload.file.read(1024)
        if not buf:
            break
        of.write(buf)

print 'done'
EOF
chmod 0700 /home/ubuntu/.i2p/eepsite/cgi-bin/upload.cgi
chown ubuntu:ubuntu /home/ubuntu/.i2p/eepsite/cgi-bin/upload.cgi

# 2) setup torrents folder
mkdir /home/ubuntu/.i2p/eepsite/docroot/torrents
chmod 0700 /home/ubuntu/.i2p/eepsite/docroot/torrents
chown ubuntu:ubuntu /home/ubuntu/.i2p/eepsite/docroot/torrents

# 3) remove index.html
rm /home/ubuntu/.i2p/eepsite/docroot/index.html
