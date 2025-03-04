#!/bin/bash
pushd /home/ubuntu

# Add Configuration Settings for i2p Client Tunnels

# Set Client Tunnel Quantities to MAXIMUM Numbers to reduce Router's Reliability
sed -i '0,/^tunnel.0.startOnLoad.*/s/^tunnel.0.startOnLoad.*/tunnel.0.option.inbound.quantity=6\n&/' .i2p/i2ptunnel.config
sed -i '0,/^tunnel.0.startOnLoad.*/s/^tunnel.0.startOnLoad.*/tunnel.0.option.outbound.quantity=6\n&/' .i2p/i2ptunnel.config
sed -i '0,/^tunnel.0.startOnLoad.*/s/^tunnel.0.startOnLoad.*/tunnel.0.option.inbound.backupQuantity=3\n&/' .i2p/i2ptunnel.config
sed -i '0,/^tunnel.0.startOnLoad.*/s/^tunnel.0.startOnLoad.*/tunnel.0.option.outbound.backupQuantity=3\n&/' .i2p/i2ptunnel.config

# Reload Configuration files
#kill -HUP $( cat /var/run/i2pd/i2pd.pid )

popd
