#!/bin/bash

pushd /home/ubuntu

# Start I2P, wait for a netdb .dat file to be created, then copy it over
sudo -u ubuntu -H i2prouter start

until ls .i2p/netDb; do echo "Waiting for i2p dir..."; sleep 1; done

pushd .i2p/netDb

i=0
until find -name '*.dat' | grep dat; do
    echo "Waiting for .dat file..."; sleep 5;
    ((i++))
    if [ "$i" -eq 5 ]; then
        echo "After waiting a brutal 25 sec, killing and restarting i2p"
        sudo -u ubuntu -H i2prouter restart
        echo "Restarted, waiting 5 sec for .dat file"
        sleep 5
        i=0
    fi
done

popd

until sudo -u ubuntu -H scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -oConnectTimeout=5 -r .i2p/netDb i2pbootstrap.internet.net: ; do echo "Waiting for scp..."; sleep 5; done

# Stop the router
sudo -u ubuntu -H i2prouter stop

popd

