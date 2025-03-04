#!/usr/bin/env python
# This agent pulls data from the http://127.0.0.1:7657/summaryframe

import sys
import json
import time
import logging
from datetime import datetime

from httplib import BadStatusLine
from urllib2 import URLError, HTTPError, urlopen

log = logging.getLogger("tunnels")
# If you want to log to a file, add filename = "log file" to call.
logging.basicConfig(filename="/home/ubuntu/tunnels.log")
log.level = logging.INFO
log.debug("Running tunnels agent")


from HTMLParser import HTMLParser


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._reset_state()
        self.seen_tunnels = []

    def _reset_state(self):
        self.state = {}
        self.state["tag"] = []
        self.report = {"agent": "tunnels"}
        self.state["section"] = ""
        self.state["NetDb entry"] = False
        self.state["look for tunnel"] = False

    def handle_starttag(self, tag, attrs):
        """Process HTML start tags:
        Look for <td> tags that are followed by <a> tags that
        have targeted key names in them. Set a status bit when you hit it.
        """
        self.state["tag"].insert(0, tag)
        ad = dict(attrs)
        if tag == "tr":
            self.state["node_ids"] = []  # Will have row of netdb entries
            self.state["tunids"] = []
        if tag == "a":
            if ad.get("title") == "NetDb entry":
                self.state["NetDb entry"] = True
            title = ad.get("title")
            if title and "I2P router identity" in title:
                self.state["nodeID"] = ad["title"].split()[6]
        if tag == "img":
            if ad.get("alt") == "Inbound":
                self.state["direction"] = "Inbound"
            if ad.get("alt") == "Outbound":
                self.state["direction"] = "Outbound"

    def handle_endtag(self, tag):
        self.state["tag"].pop(0)
        if tag == "tr" and self.state["node_ids"]:
            # Now we have enough data to record the data
            self.report_tunnel_if_new()

    def handle_data(self, data):
        """Looks for various key/value pairs that are in the web page
        and extracts out the values and then has methods add them
        to the report data.
        """
        if not self.state["tag"]:
            return
        # if self.state['tag'][0] == 'a':
        if self.state["tag"][0] == "h2":
            if "Exploratory tunnels" in data:
                self.state["section"] = "exploratory"
            elif "Client tunnels for eepsite" in data:
                self.state["section"] = "eepsite"
            elif "Client tunnels for shared clients (DSA)" in data:
                self.state["section"] = "shared clients (DSA)"
            elif "Client tunnels for shared clients" in data:
                self.state["section"] = "shared clients"
            elif "Participating tunnels" in data:
                self.state["section"] = "participating"

        # Data is the shortened name in the NetDb database.
        if self.state["NetDb entry"]:
            if self.state["section"] in {
                "exploratory",
                "eepsite",
                "shared clients (DSA)",
            }:
                self.state["node_ids"].append(data)
                self.state["NetDb entry"] = False
                self.state["look for tunnel"] = True

        # Trying to find the tunnel number
        if self.state["look for tunnel"]:
            if self.state["tag"][0] == "td" or self.state["tag"][0] == "img":
                try:
                    tunid = data.split()[0]
                    self.state["tunids"].append(tunid)
                except:
                    tunid = "Unexpected"
                self.state["look for tunnel"] = False

    def report_tunnel_if_new(self):
        """Sees if tunnel is new. If it is, forms a report on it."""
        tunid = "-".join(self.state["tunids"])
        if tunid not in self.seen_tunnels:
            if len(self.state["tunids"]) > 0:
                d = {}
                d["agent"] = "tunnels"
                d["Router ID"] = self.state["nodeID"].strip(",")
                d["Tunnel type"] = self.state["section"]
                d["Node IDs"] = self.state["node_ids"]
                d["Node Chain"] = "-".join(self.state["node_ids"])
                d["Direction"] = self.state["direction"]
                if self.state["direction"] == "Inbound":
                    d["Gateway"] = self.state["node_ids"][0]
                else:
                    d["Endpoint"] = self.state["node_ids"][-1]
                d["TunnelID"] = tunid
                d["Time"] = datetime.now().isoformat()
                self.log_dict(d)
                self.logcnt += 1
                if self.logcnt == 12:
                    sys.exit()
                self.seen_tunnels.append(tunid)

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
            url = "http://127.0.0.1:7657/tunnels"
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
        self.logcnt = 0
        while True:
            self._reset_state()
            html = self.get_summaryframe()
            if html:
                # Feed is a base method from HTMLParser
                self.feed(html)
            else:
                self.log_error("NoData", "No data read from tunnels")
            time.sleep(5)


# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
if 0:
    # Test code for working from local files
    for fname in [
        "samples/tunnel_summary_eepsite.html",
        "samples/tunnel_summary_eepsite2.html",
        "samples/tunnel_summary.html",
        "samples/tunnel_summary2.html",
    ]:
        fp = open(fname, "r", encoding="utf-8")
        html = fp.read()
        if html:
            print("Parsing", fname)
            parser.feed(html)

else:
    parser.run()
