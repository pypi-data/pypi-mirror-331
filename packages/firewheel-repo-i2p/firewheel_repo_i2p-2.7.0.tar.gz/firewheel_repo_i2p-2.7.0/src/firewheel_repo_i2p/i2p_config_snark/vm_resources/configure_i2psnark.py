#!/usr/bin/env python

import sys
import json


class ConfigureI2PSnark(object):
    def __init__(self, ascii_file, binary_file, reboot_file):
        self.ascii_file = ascii_file
        self.binary_file = binary_file
        self.reboot_file = reboot_file

    def run(self):
        with open(self.ascii_file, "r", encoding="utf-8") as f:
            conf = json.load(f)

        up_bw = conf["upbw_max"]
        print("Loaded desired upbw_max: %s" % up_bw)
        i2psnark_config = "/home/ubuntu/.i2p/i2psnark.config.d/i2psnark.config"
        print("Using I2PSnark config at %s" % i2psnark_config)

        found = False
        with open(i2psnark_config, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for l in lines:
            if l.startswith("i2psnark.upbw.max"):
                l = "i2psnark.upbw.max=%s" % up_bw
                found = True
                print("Found existing upbw.max in config file: %s" % l)
        if not found:
            print("Adding new upbw.max line: %s" % int(up_bw))
            lines.append("i2psnark.upbw.max=%s\n" % int(up_bw))

        lines.append("i2psnark.autoStart=true\n")
        # lines.append('i2psnark.uploaders.total=500\n')

        with open(i2psnark_config, "w", encoding="utf-8") as f:
            print("Writing new I2PSnark config at %s" % i2psnark_config)
            f.write("".join(lines))


if __name__ == "__main__":
    a = sys.argv[1]
    b = sys.argv[2]
    r = sys.argv[3]

    configurer = ConfigureI2PSnark(a, b, r)
    configurer.run()
