#!/usr/bin/env python
import sys
import json
import time
import random
import socket
import urllib
import subprocess

import urllib2


class GenerateTorrent(object):
    """
    Agent that will generate torrent content at random times
    and add them to the tracker.

    ASCII input data structure:
    {
        # Example file to append config parameters for
        'gen_freq' : <frequency to generate files>,
        'gen_size_min'  : <minimum size of content>,
        'gen_size_max'  : <maximum size of content>,
        'tracker_name'  : <Name of tracker to use>,
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
        with open("/tmp/gen-status", "w", encoding="utf-8") as f:
            f.write("waiting")
        try:
            with open("/mytrack.i2p", encoding="utf-8") as f:
                f.readline()
        except:
            time.sleep(30)
        with open("/tmp/gen-status", "w", encoding="utf-8") as f:
            f.write("started")

        with open(self.ascii_file, "r", encoding="utf-8") as af:
            self.settings_file = json.load(af)
        min_size = self.settings_file["gen_size_min"]
        max_size = self.settings_file["gen_size_max"]
        interarrival_time = self.settings_file["gen_freq"]
        self.tracker_name = self.settings_file["tracker_name"]
        # self.torrent_upload_url = self.settings_file['torrent_upload_url']

        # Over a period of time, generate and seed N('range') number of random binary torrent files
        for _ in range(50):
            # Wait so long
            sleep_time = random.expovariate(1.0 / interarrival_time)
            time.sleep(sleep_time)

            # Create file
            size = int(random.uniform(min_size, max_size))
            fname = self.gen_file(size)

            # Make a torrent file
            self.create_torrent(fname)

            # Upload to torentzz
            self.upload_torrent_file(fname)

            # Start seeding the torrent file
            self.start_seeding()

    def start_seeding(self):
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

    def create_torrent(self, fname):
        tracker = ""
        nonce = ""
        while tracker == "":
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
                if self.tracker_name in l and "announceURL" in l:
                    for z in l.split():
                        if self.tracker_name in z and "http" in z and "backup" not in z:
                            tracker = z.split('"')[1]
                if "mytrack" in l and "announceURL" in l:
                    for z in l.split():
                        if "http" in z and "announce.php" in z and "backup" not in z:
                            full_tracker = z.split('"')[1]

        data = (
            "nonce=%s&action=Create&nofilter_baseFile=%s&foo=Create+torrent&announceURL=%s&backup_%s=foo"
            % (nonce, fname, urllib.quote(full_tracker), urllib.quote(tracker))
        )

        content = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/?%s" % data)
        # fixme needs error checking / retry

    def upload_torrent_file(self, fname):
        tname = fname.split("/")[-1]

        # get the magnet url
        mag = ""
        while mag == "":
            u = urllib2.urlopen("http://127.0.0.1:7657/i2psnark/%s/" % tname)
            ret = u.read()
            for x in ret.split('"'):
                if "magnet:?xt=urn:" in x:
                    mag = x.replace("&amp;", "&")
                    break

        tpath = "/home/ubuntu/%s.magnet" % tname

        with open(tpath, "w", encoding="utf-8") as f:
            f.write("%s\n" % mag)

        # cmd = ['curl', '-F', 'file=@%s@' % fname, self.torrent_upload_url]
        cmd = [
            "scp",
            "-oConnectTimeout=10",
            tpath,
            "superhidden-bttrack.internet.net:/srv/torrents/",
        ]
        while subprocess.call(cmd) != 0:
            time.sleep(20)

    def gen_file(self, size):
        fname = "/tmp/%s-torrent-%d" % (socket.gethostname(), self.file_count)
        print("Writing %d to %s" % (size, fname))
        inf = open("/dev/urandom", "r", encoding="utf-8")
        ouf = open(fname, "w", encoding="utf-8")
        ouf.write(inf.read(size))
        inf.close()
        ouf.close()
        self.file_count += 1
        return fname


if __name__ == "__main__":
    gt = GenerateTorrent(sys.argv[1], sys.argv[2])
    gt.run()
