#!/usr/bin/env python
# This agent pulls data from the http://127.0.0.1:7657/summaryframe

import sys
import copy
import json
import time
import logging

from httplib import BadStatusLine
from urllib2 import URLError, HTTPError, urlopen

log = logging.getLogger("summaryframe")
# If you want to log to a file, add filename = "log file" to call.
logging.basicConfig(filename="/home/ubuntu/summaryframe.log")
log.level = logging.INFO
log.debug("Running summaryframe agent")


from HTMLParser import HTMLParser


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state = {}
        self.state["tag"] = []
        self.state["status"] = None
        self.report = {"agent": "summaryframe"}
        self.dual_value_targets = {
            "Active": ["Active peers (last min)", "Active peers (last hr)"],
            "sec:": ["In Bandwidth (3 sec)", "Out Bandwidth (3 sec)"],
            "min:": ["In Bandwidth (5 min)", "Out Bandwidth (5 min)"],
            "Total": ["In Bandwidth (total)", "Out Bandwidth (total)"],
        }
        self.single_value_targets = {
            "Fast": "Fast peers",
            "High capacity": "High capacity peers",
            "Integrated": "Integrated peers",
            "Known": "Known peers",
            "Exploratory": "Exploratory tunnels",
            "Client": "Client tunnels",
            "Participating": "Participating tunnels",
            "Share ratio": "Tunnel share ratio",
        }
        self.targets = copy.deepcopy(self.dual_value_targets)
        self.targets.update(self.single_value_targets)

    def handle_starttag(self, tag, attrs):
        """Process HTML start tags:
        Look for <td> tags that are followed by <a> tags that
        have targeted key names in them. Set a status bit when you hit it.
        """
        self.state["tag"].insert(0, tag)
        if tag == "td":
            for target in self.targets:
                if self.state["status"] == target:
                    self.state["status"] = target + "-td"

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        self.state["tag"].pop(0)

    def handle_data(self, data):
        """Looks for various key/value pairs that are in the web page
        and extracts out the values and then has methods add them
        to the report data.
        """

        if not self.state["tag"]:
            return

        for target in self.targets:
            if target in data:
                # "Target", target, "in data"
                self.state["status"] = target
                break

        # Network shows up differently than everything else.
        if "Network" in data:
            self.report["Network"] = " ".join(data.split(": ")[1:])

        for target in self.dual_value_targets:
            goal = target + "-td"
            if self.state["status"] == goal:
                self.report_two(self.dual_value_targets[target], data)
                self.state["status"] = None
                break
        if self.state["status"]:
            for target in self.single_value_targets:
                goal = target + "-td"
                if self.state["status"] == goal:
                    self.report_one(self.single_value_targets[target], data)
                    self.state["status"] = None
                    break

        # TODO: Make this block work
        if False and self.state["tag"][0] == "a":
            if "Your unique I2P router identity is" in data:
                # node_id = data.split()[6]
                print("node_id", data.split())

        if self.state["tag"][0] == "p":
            if "This router is currently a floodfill participant" in data:
                self.report["floodfill"] = True

    def report_two(self, titles, data):
        vals = data.split(" / ")
        self.report[titles[0]] = self.number(vals[0])
        self.report[titles[1]] = self.number(vals[1])

    def report_one(self, title, data):
        self.report[title] = self.number(data)

    def number(self, data):
        """Convert string (data) into a float, int or leave as string"""
        try:
            v = int(data)
        except:
            try:
                v = float(data)
            except:
                v = data
        return v

    def log_dict(self, d):
        """Logs d, assumed to be a dict, in json format"""
        try:
            report = json.dumps(d)
            sys.stdout.write("%s\n" % report)
            sys.stdout.flush()
        except:
            print("Error dumping report", d)

    def log_error(self, source, msg="", dict=None):
        """Logs (prints) an error message where
        source is the source (method name) of the error
        msg is a message that will be sent (Only one message please)
        """
        if dict is None:
            dict = {}
        d = {"Error": source}
        if msg:
            d["description"] = str(msg)
        if dict:
            d.update(dict)
        t, _v, _tb = sys.exc_info()
        if t:
            d["type"] = str(t)
        self.log_dict(d)

    def get_summaryframe(self):
        """Gets the data from summaryframe on localhost"""
        try:
            # Log *before* trying the URL, so we can tell what's happening.
            log.debug("Reading summary I2P data.")
            # summaryframe just has the summary frame.
            # configadvanced has the "floodfill configuration"
            url = "http://127.0.0.1:7657/configadvanced"
            obj = urlopen(url, timeout=5)
            return obj.read()
        except HTTPError as e:
            if e.code == 304:
                # Schedule has not changed since last version.
                log.debug("Error 304: No changes to schedule data ")
            else:
                self.log_error("HTTPError", e)
        except BadStatusLine as e:
            self.log_error("BadStatusLine", e)
        except URLError as e:
            self.log_error("URLError", e)
        except Exception as e:
            self.log_error("Unknown", e)
        return None

    def run(self):
        """Runs agent
        Attempts to poll summary frame every 5 seconds and prints results if successful
        """
        logcnt = 0
        while True:
            self.report = {"agent": "summaryframe"}
            self.report["floodfill"] = False
            html = self.get_summaryframe()
            if html:
                # Feed is a base method from HTMLParser
                self.feed(html)
                parser.log_dict(self.report)
                logcnt += 1
                if logcnt == 3:
                    sys.exit()
            else:
                self.log_error("NoData", "No data read from statusframe")
            time.sleep(5)


# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
if 0:
    # Test code for working from local files
    for fname in ["samples/summaryframe.html", "samples/tunnel_summary.html"]:
        fp = open(fname, "r", encoding="utf-8")
        html = fp.read()
        if html:
            parser.feed(html)
            import pprint

            print("results")
            pprint.pprint(parser.report)
            parser.log_dict(parser.report)
else:
    parser.run()
