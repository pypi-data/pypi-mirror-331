#!/usr/bin/env python

# In the future, could parameterize this
# For now, it is hardcoded to only work with tracktor

import time

import urllib2
import mechanize


def main():
    # Try to get the base64 address
    b64a = ""
    while b64a == "":
        try:
            url = urllib2.urlopen(
                "http://superhidden-bttrack.internet.net:9998/tracktor.i2p"
            )
            b64a = url.read().strip()
        except:
            time.sleep(30)

    br = mechanize.Browser()
    br.open("http://127.0.0.1:7657/susidns/addressbook?book=master&filter=none")

    br.select_form(nr=0)

    br["hostname"] = "tracktor.i2p"
    br["destination"] = b64a

    br.submit()


if __name__ == "__main__":
    main()
