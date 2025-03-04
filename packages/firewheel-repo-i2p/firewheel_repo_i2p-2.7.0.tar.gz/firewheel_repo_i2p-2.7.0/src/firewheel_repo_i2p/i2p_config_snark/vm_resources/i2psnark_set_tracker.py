#!/usr/bin/env python

import json
from sys import argv


class I2PSnarkSetTracker(object):
    def __init__(self, ascii_file=None, binary_file=None, reboot_file=None):
        self.conf_file = ascii_file

    def run(self):
        """
        Run the agent: Append the tracker info to the list of trackers.
        """
        self.set_tracker()

    def set_tracker(self):
        # Load the ASCII configuration file.
        with open(self.conf_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        filename = config["filename"]
        tracker_name = config["tracker_name"]
        website_url = config["website_url"]
        announce_url = config["announce_url"]

        # Read the configuration file.
        with open(filename, "r", encoding="utf-8") as f:
            conf = f.read()

        # Append the tracker to list of trackers
        out = ""
        if "i2psnark.trackers" in conf:
            for line in conf.split("\n"):
                if string.find(line, "i2psnark.trackers") == 0:
                    line += ",%s,%s=%s" % (tracker_name, announce_url, website_url)
                out += line + "\n"
        else:
            conf += "\ni2psnark.trackers=%s,%s=%s\n" % (
                tracker_name,
                announce_url,
                website_url,
            )
            out = conf

        with open(filename, "w", encoding="utf-8") as f:
            f.write(out)


if __name__ == "__main__":
    if len(argv) >= 1:
        ascii_arg = argv[1]
        reboot_arg = None
    else:
        binary_arg = None
        reboot_arg = None

    I2PConf = I2PSnarkSetTracker(ascii_arg)
    I2PConf.run()
