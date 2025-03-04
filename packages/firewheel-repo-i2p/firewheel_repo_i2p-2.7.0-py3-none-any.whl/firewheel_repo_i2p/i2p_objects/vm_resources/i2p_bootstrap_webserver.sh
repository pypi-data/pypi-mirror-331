#!/bin/bash

mkdir -p /srv
pushd /home/ubuntu
tar czf netdb.tgz netDb
popd

mv /home/ubuntu/netdb.tgz /srv/


if [[ `grep "16.04" /etc/os-release` ]];
then
    cat >/opt/serve.sh <<EOF
#!/bin/bash
pushd /srv
busybox httpd -f -p 9998
EOF
    chmod +x /opt/serve.sh
    cat >/etc/systemd/system/bootsrv.service <<EOF
[Unit]
Description=bootsrv
After=network.target
[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=/opt/serve.sh

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl start bootsrv
    systemctl enable bootsrv

else

    cat >/etc/init/bootsrv.conf <<EOF
description "bootsrv"

start on filesystem or runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5
umask 022

script
chdir /srv
busybox httpd -f -p 9998
end script
EOF
    ln -s /lib/init/upstart-job /etc/init.d/bootsrv

    service bootsrv start

fi
