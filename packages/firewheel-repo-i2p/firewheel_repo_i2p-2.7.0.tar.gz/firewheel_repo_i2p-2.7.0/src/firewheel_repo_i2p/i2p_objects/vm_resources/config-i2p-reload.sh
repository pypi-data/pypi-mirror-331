#!/bin/bash
pushd /home/ubuntu

# Restart the i2p Router if it's running,
# so it'll Reload i2p Configuration files
i2prouter condrestart

popd
