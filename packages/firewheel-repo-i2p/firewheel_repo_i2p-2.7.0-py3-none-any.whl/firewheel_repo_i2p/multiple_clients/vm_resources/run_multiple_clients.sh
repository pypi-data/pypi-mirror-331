#!/bin/bash

# Wait for get-netdb.sh to finish
until [ -d /tmp/get-netdb-finished ]; do
    echo "Waiting for get-netdb to finish"
    sleep $((RANDOM%10))
done

NUM_CLIENTS=$1

# Setup the given number of i2p routers
for N in $(seq 1 $NUM_CLIENTS); do
    user="u-i2p$N"
    userc="sudo -u $user -i"
    ns="ns-i2p$N"
    nse="ip netns exec $ns"

    # Add in the main netDb entries
    cp -r /home/ubuntu/.i2p/netDb/* /home/$user/.i2p/netDb
    chown $user:$user -R /home/$user/.i2p/netDb

    # Finally, start the router again
    $nse $userc i2prouter start

    # Start a client
    $nse $userc /multi-client.sh &

    # Stagger the startups
    sleep 20
done
