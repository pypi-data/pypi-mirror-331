#!/bin/bash
pushd /home/ubuntu

# Add Configuration Settings for i2p Client Tunnels

# Set Client Tunnels to MAX Lengths (4) and MAX Variance (2) to reduce Router's Reliability
sed -i 's/^tunnel.0.option.inbound.length=.*/tunnel.0.option.inbound.length=4/' .i2p/i2ptunnel.config
sed -i 's/^tunnel.0.option.outbound.length=.*/tunnel.0.option.outbound.length=4/' .i2p/i2ptunnel.config
sed -i 's/^tunnel.0.option.inbound.lengthVariance=.*/tunnel.0.option.inbound.lengthVariance=2/' .i2p/i2ptunnel.config
sed -i 's/^tunnel.0.option.outbound.lengthVariance=.*/tunnel.0.option.outbound.lengthVariance=2/' .i2p/i2ptunnel.config

# Reload Configuration files
#kill -HUP $( cat /var/run/i2pd/i2pd.pid )

popd
