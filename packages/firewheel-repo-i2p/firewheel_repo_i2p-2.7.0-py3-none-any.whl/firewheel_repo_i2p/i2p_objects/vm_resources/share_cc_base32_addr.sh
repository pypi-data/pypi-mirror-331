#!/bin/bash

until grep b32 /srv/address; do
    wget -O i2ptunnel.html 'http://127.0.0.1:7657/i2ptunnel/'
    grep b32 i2ptunnel.html | awk '{print $8}' | grep href | sed 's/href="//' | sed 's/"//' | head -1 > /srv/address
    sleep 10
done

