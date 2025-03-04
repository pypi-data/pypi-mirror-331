#!/bin/bash
pushd /home/ubuntu

# Turn on logging for i2p client activity ground truth data capture

echo "logger.record.net.i2p.router.networkdb.kademlia.KademliaNetworkDatabaseFacade=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.networkdb.kademlia.FloodfillNetworkDatabaseFacade=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.networkdb.kademlia.HandleFloodfillDatabaseStoreMessageJob=DEBUG" >> .i2p/logger.config

echo "logger.record.net.i2p.router.networkdb.PublishLocalRouterInfoJob=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.networkdb.kademlia.FloodfillStoreJob=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.networkdb.kademlia.StoreJob=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.networkdb.HandleDatabaseLookupMessageJob=DEBUG" >> .i2p/logger.config

echo "logger.record.net.i2p.router.networkdb.kademlia.FloodfillVerifyStoreJob=DEBUG" >> .i2p/logger.config
echo "logger.record.net.i2p.router.tunnel.TunnelDispatcher=DEBUG" >> .i2p/logger.config

# Only allow one log file to be used i.e. no log filename rotation

echo "logger.logRotationLimit=1" >> .i2p/logger.config
echo "logger.logFileSize=20M" >> .i2p/logger.config

popd
