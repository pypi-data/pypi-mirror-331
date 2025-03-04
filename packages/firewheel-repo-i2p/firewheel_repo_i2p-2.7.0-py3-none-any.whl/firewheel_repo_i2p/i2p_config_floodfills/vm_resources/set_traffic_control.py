#!/usr/bin/python
import sys
import json
import time
import shlex
import subprocess as sp

# Usage: set_traffic_control.py <config>
#
#        config = a json dictionary containing required rate and rate_value key:value
#                 pairs and optionally ceil, burst, and/or cburst keys:valur pairs
#
# set traffic firewheel.control.(tc) on dev eth1 using passed in values


def main():
    # Read arguments from json file
    # (fname passed in sys.argv[1])
    with open(sys.argv[1], "r", encoding="utf-8") as af:
        args = json.load(af)

    # Get the tc command to execute [add, replace]
    cmd = args["cmd"]

    # Get the rate and rate_value settings from the config dict
    rate = int(args["rate"])
    rate_unit = args["rate_unit"]

    # Get/set optional arguments
    if "ceil" in args:
        ceil = int(args["ceil"])
    else:
        ceil = rate
    if "burst" in args:
        burst = int(args["burst"])
    else:
        burst = rate / 2
    if "cburst" in args:
        cburst = int(args["cburst"])
    else:
        cburst = burst

    response = ""

    if cmd == "add":
        # run tc qdisc command
        p = sp.Popen(
            shlex.split(
                "sudo tc qdisc %s dev eth1 root handle 1: htb default 1" % (cmd,)
            ),
            stdout=sp.PIPE,
        ).wait()
        print("sudo tc qdisc %s dev eth1 root handle 1: htb default 1" % (cmd,))

        # sleep a bit to allow qdisc add command to complete
        time.sleep(3)

    # run tc class command
    p = sp.Popen(
        shlex.split(
            "sudo tc class %s dev eth1 parent 1: classid 0:1 htb rate %d%s ceil %d%s burst %d%s cburst %d%s"
            % (
                cmd,
                rate,
                rate_unit,
                ceil,
                rate_unit,
                burst,
                rate_unit,
                cburst,
                rate_unit,
            )
        ),
        stdout=sp.PIPE,
    ).wait()
    print(
        "sudo tc class %s dev eth1 parent 1: classid 0:1 htb rate %d%s ceil %d%s burst %d%s cburst %d%s"
        % (cmd, rate, rate_unit, ceil, rate_unit, burst, rate_unit, cburst, rate_unit)
    )

    # all done
    return 0


if __name__ == "__main__":
    main()
