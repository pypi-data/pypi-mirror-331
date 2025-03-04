#!/usr/bin/env python
import os
import sys
import json
import time
import os.path

import urllib2


class CreateTunnel(object):
    """
    Agent that will create tunnels in i2p hidden services

    ASCII input data structure:
    {
        # Example file to append config parameters for
        'name' : Friendly name of tunnel (eg. Tracktor)
        'website_name'  : name of tunnel website (eg. Tracktor.i2p)
        'port'  : port number of service (eg. 6969)
        'number_of_tunnels'  : number of in/out tunnels for service (default = 2)
    }
    """

    def __init__(self, ascii_file=None, binary_file=None):
        """
        Constructor for the class. Pass in standard agent parameters

        Parmeters:
            ascii_file: the dictionary of dictionaries specified above
            binary_file: None
        """
        self.ascii_file = ascii_file
        self.binary_file = binary_file
        if binary_file == "None":
            self.binary_file = None
        self.file_count = 0

    def run(self):
        """
        Standard agent run function. This performs the work of the agent.
        Requires no parameters, since they are passed into __init__()
        """
        with open(self.ascii_file, "r", encoding="utf-8") as af:
            settings_file = json.load(af)
        name = settings_file["name"]
        website_name = settings_file["website_name"]
        port = settings_file["port"]
        number_of_tunnels = settings_file["number_of_tunnels"]

        # Make sure i2p is started
        print("Waiting on get netDb")
        while not os.path.isdir("/tmp/get-netdb-finished"):
            time.sleep(5)
        print("Making tunnel")

        # Make the tunnel
        self.create_tunnel(name, website_name, port, number_of_tunnels)

    def create_tunnel(self, name, website_name, port, number_of_tunnels):
        tunlist = ""
        while name not in tunlist:
            if tunlist != "":
                print("Waiting to try again")
                time.sleep(30)
            nonce = None

            while nonce is None:
                content = urllib2.urlopen(
                    "http://127.0.0.1:7657/i2ptunnel/edit?=type=httpserver"
                )
                ret = content.read()

                for l in ret.split("\n"):
                    if "nonce" in l:
                        n = l.split()[3].split('"')[1]
                        try:
                            int(n)
                            nonce = n
                        except:
                            print("Waiting")
                            time.sleep(15)
                            continue

            data = (
                "tunnel=-1&nonce=%s&type=httpserver&name=%s&nofilter_description=&startOnLoad=1&targetHost=127.0.0.1&targetPort=%s&spoofedHost=%s&privKeyFile=i2ptunnel8-privKeys.dat&tunnelDepth=3&tunnelVariance=0&tunnelQuantity=%s&tunnelBackupQuantity=0&profile=bulk&clientHost=internal&clientport=internal&encryptKey=&accessMode=0&accessList=&limitMinute=0&limitHour=0&limitDay=0&totalMinute=0&totalHour=0&totalDay=0&maxStreams=0&postMax=0&postBanTime=30&postTotalMax=0&postTotalBanTime=10&postCheckTime=5&reduceCount=1&reduceTime=20&sigType=1&nofilter_customOptions=&removeConfirm=true&action=Save+changes"
                % (nonce, name, port, website_name, number_of_tunnels)
            )

            content = urllib2.urlopen("http://127.0.0.1:7657/i2ptunnel/list?%s" % data)
            tunlist = content.read()


if __name__ == "__main__":
    ct = CreateTunnel(sys.argv[1], sys.argv[2])
    ct.run()
