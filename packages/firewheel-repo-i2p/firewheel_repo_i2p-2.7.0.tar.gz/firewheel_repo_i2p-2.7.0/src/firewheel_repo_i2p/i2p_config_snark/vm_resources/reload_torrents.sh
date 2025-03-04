#!/bin/bash

while [ 1 ]; do

    files="$(wget --timeout 30 -O- 'http://127.0.0.1:7657/i2psnark/?sort=2' 2>/dev/null | grep -A2 'Tracker Error' | grep 'Torrent details' | cut -d' ' -f2 | sed 's/href=.//' | sed 's/\/"$//')"

    for x in $files; do
        mv /home/ubuntu/.i2p/i2psnark/$x.torrent /tmp
    done
    # Wait for the torrent to be removed
    sleep 30
    for x in $files; do
        if ! grep announce-list /tmp/$x.torrent; then
            # Patch the full announce-list in, adding in the backup tracker
            head="$(grep -o -E 'd8:announce.*4:infod' /tmp/$x.torrent | sed 's/4:infod//')"
            full_size=$(wc -c /tmp/$x.torrent | awk '{print $1}')
            head_size=$(echo $head | wc -c | awk '{print $1}')
            ((tail_size=full_size-head_size+1))
            tail -c $tail_size /tmp/$x.torrent > /tmp/$x.tail

            ptrack="$(echo $head | sed 's/d8:announce//')"

            echo $head > /tmp/$x.stage
            echo 13:announce-listll >> /tmp/$x.stage
            echo $ptrack >> /tmp/$x.stage
            echo "el32:http://tracktor.i2p/announce.phpee" >> /tmp/$x.stage
            cat /tmp/$x.stage /tmp/$x.tail > /tmp/$x.torrent
        fi
        # Add the torrent back
        mv /tmp/$x.torrent /home/ubuntu/.i2p/i2psnark/
    done

    # Wait 2 minutes
    sleep 120

done
