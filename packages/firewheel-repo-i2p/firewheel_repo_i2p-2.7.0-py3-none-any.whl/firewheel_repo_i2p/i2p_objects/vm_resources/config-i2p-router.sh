#!/bin/bash
pushd /home/ubuntu

# Add Configuration Settings for i2p Routers

# Verify that its RouterInfo was Flooded to the netDb after Publishing it.
echo "router.verifyRouterInfoStore=true" >> /usr/share/i2p/router.config

popd
