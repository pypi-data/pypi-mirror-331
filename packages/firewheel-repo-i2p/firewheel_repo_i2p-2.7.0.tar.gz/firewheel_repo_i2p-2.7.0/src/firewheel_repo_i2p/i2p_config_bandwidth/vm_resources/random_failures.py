#!/usr/bin/env python
import sys
import json
import time
import random
import socket
import subprocess as sp


class RandomFailure(object):
    """
    Agent that will cause i2p to shutdown and restart at random times
    that are exponentially distributed on a per node basis.

    ASCII input data structure:

    {
        # Example file to append config parameters for
        'mean_lifetime' : <mean of lifetime>,
        'mean_offtime'  : <mean of offtime>
    }

    """

    def __init__(self, ascii_file=None, binary_file=None):
        """
        Constructor for the class. Pass in standard agent parameters

        Parmeters:
            ascii_file: json structure containing config parameters
            binary_file: None
        """
        self.ascii_file = ascii_file
        self.binary_file = binary_file
        if binary_file == "None":
            self.binary_file = None

    def run(self):
        """
        Standard agent run function. This performs the work of the agent.
        Requires no parameters, since they are passed into __init__()
        """
        self.settings = None
        with open(self.ascii_file, "r", encoding="utf-8") as f:
            self.settings = json.loads(f.read())
        assert self.settings is not None

        # Log startup to Kibana
        self.log("announce")

        if dcontains(settings_file, "deterministic"):
            if dcontains(settings_file, "fail_time"):
                # Wait fail_time before starting
                time.sleep(float(settings_file["fail_time"]))
                cmd = "i2prouter stop"
                # Log to Kibana
                msg = {}
                self.log("failure")

        else:
            # As long as this experiment runs, keep going up and down
            while True:
                # Pick an amount of time to live before failing
                p_param = float(settings_file["mean_lifetime"])
                fail_time = random.expovariate(1.0 / p_param)
                time.sleep(fail_time)
                cmd = "i2prouter stop"
                # Log to Kibana
                self.log("failure")

                # Pick an amount of time to be offline for
                p_param = float(settings_file["mean_offtime"])
                restore_time = random.expovariate(1.0 / p_param)
                time.sleep(restore_time)
                cmd = "i2prouter start"
                self.log("restart")

    def log(self, msg_string):
        # Log to Kibana
        msg = {}
        msg["message"] = "i2p_router_fail %s" % (msg_string)
        msg["host"] = socket.gethostname()

        for attr in [
            "mean_lifetime",
            "mean_offtime",
            "actual_lifetime",
            "actual_offtime",
            "deterministic",
            "fail_time",
        ]:
            if dcontains(self.settings, attr):
                msg[attr] = self.settings[attr]

        sys.stdout.write("%s\n" % json.dumps(msg))
        sys.stdout.flush()

        sp.call(shlex.split(cmd))


def dcontains(d, attr):
    return attr in d and d[attr]


if __name__ == "__main__":
    rf = RandomFailure(sys.argv[1], sys.argv[2])
    rf.run()
