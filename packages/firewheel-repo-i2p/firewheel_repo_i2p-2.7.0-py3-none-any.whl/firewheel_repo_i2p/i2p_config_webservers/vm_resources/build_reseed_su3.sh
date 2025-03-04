#!/bin/bash

until test -d /home/ubuntu/netDb; do echo "Waiting for NetDb..."; sleep 1; done

pushd /opt/reseed

# Wait for the NetDb to have 60 entries
# TODO: Make this configurable
pushd /home/ubuntu/netDb
#while [ $(find -name '*.dat' | grep dat | wc -l) -le 60 ]
while [ $(find -name '*.dat' | grep dat | wc -l) -le 5 ]
do
    echo "Not enough router infos yet..."
    sleep 5
done

# Build a subdirectory to hold our router infos.
mkdir -p /opt/i2p/bootstrap

# Copy router infos into the directory.
find -name '*.dat' | grep dat | xargs -I{} -n 1 cp {} /opt/i2p/bootstrap
popd

# Zip our router infos
# According to the I2P reseed specification, the router infos need to be in the
# same directory (on the web server) as the SU3 file. So, use the web root to
# generate our files
pushd /opt/i2p/bootstrap
zip -r routers.zip *.dat

# Build the su3 file incorporating that zip
# TODO: Make the key used here configurable.
# We have to do this with expect so we can provide the correct key password.
cat > exp.expect <<EOF
#!/usr/bin/expect

spawn java -classpath $CLASSPATH:/usr/share/i2p/lib/i2p.jar net.i2p.crypto.SU3File sign -c RESEED routers.zip /opt/i2p/bootstrap/i2pseeds.su3 /opt/reseed/meeh_at_mail.i2p.crt.ks 3 meeh@mail.i2p

expect {
    "*Enter password for key *"
}

send "password\n"

wait
EOF
expect -d -f exp.expect

# Some sites use a netDb subdirectory. Just add that in.
mkdir -p /opt/i2p/bootstrap/netDb
cp /opt/i2p/bootstrap/* /opt/i2p/bootstrap/netDb/

popd
popd
