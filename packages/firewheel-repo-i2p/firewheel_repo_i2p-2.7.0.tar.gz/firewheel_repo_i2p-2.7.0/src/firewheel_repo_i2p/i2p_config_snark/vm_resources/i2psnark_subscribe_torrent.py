#!/usr/bin/env python
import sys
import json
import time
import random
import urllib
import hashlib

import urllib2


class SubscribeTorrent(object):
    """
    Agent that will subscribe/download torrent content at random times.

    ASCII input data structure:
    {
        # Example file to append config parameters for
        'consume_freq' : <frequency to consume files>,
        'immediate_delete'  : <true/false>,
        'torrent_list_url'  : <URL of torrentzz>,
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

        self.requested = set()

    def run(self):
        """
        Standard agent run function. This performs the work of the agent.
        Requires no parameters, since they are passed into __init__()
        """
        with open(self.ascii_file, "r", encoding="utf-8") as af:
            settings_file = json.load(af)
        interarrival_time = settings_file["consume_freq"]
        torrent_list_url = settings_file["torrent_list_url"]

        # As long as this experiment runs, keep going up and down
        while True:
            # Wait so long
            sleep_time = random.expovariate(1.0 / interarrival_time)
            time.sleep(sleep_time)

            # Get list of torrents
            torrent_names = self.get_torrent_list(torrent_list_url)
            if len(torrent_names) == 0:
                continue

            # Pick a torrent to get
            torrent_url = self.pick_torrent(torrent_names)

            if torrent_url in self.requested:
                continue
            self.requested.add(torrent_url)

            # Load url into i2psnark
            self.request_torrent(torrent_url)

            # Start everything
            self.start_torrents()

    def start_torrents(self):
        content = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/")
        ret = content.read()

        for l in ret.split("\n"):
            if "nonce" in l:
                n = l.split()[3].split('"')[1]
                try:
                    int(n[:5])
                    nonce = n
                except:
                    continue
        data = "nonce=%s&action_StartAll.x=2&action_StartAll.y=2" % (nonce)
        content = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/?%s" % data)

    def get_torrent_list(self, torrent_list_url):
        try:
            content = urllib2.urlopen(torrent_list_url)
            ret = content.read()
            torrent_list = []
            for t in ret.split("\n"):
                # find link
                torrent_list.append(t)

            return torrent_list
        except:
            return []

    def request_torrent(self, torrent_url, file_location=""):
        content = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/")
        ret = content.read()

        for l in ret.split("\n"):
            if "nonce" in l:
                n = l.split()[3].split('"')[1]
                try:
                    int(n[:5])
                    nonce = n
                except:
                    continue

        data = (
            "nonce=%s&action=Add&nofilter_newURL=%s&foo=Add+torrent&nofilter_newDir="
            % (nonce, urllib.quote(torrent_url))
        )
        content = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/?%s" % data)

    def pick_torrent(self, torrent_names):
        # We want to bias towards 'popular' torrents, but with some reasonable probability pick any torrent
        # We want to sample with replacement, so if we already chose it then we will just wait for the next pick
        t = {}
        for torrent_name in torrent_names:
            h = hashlib.sha256()
            h.update(torrent_name)
            t[h.digest()] = torrent_name

        sorted_t = sorted(t.keys())
        max_val = len(sorted_t)

        # Use some distribution, here we choose beta
        pos = int(max_val * random.betavariate(1.3, 5))

        return t[sorted_t[pos]]


if __name__ == "__main__":
    st = SubscribeTorrent(sys.argv[1], sys.argv[2])
    st.run()
