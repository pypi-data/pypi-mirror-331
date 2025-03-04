#!/usr/bin/env python

import os
import sys
import pickle
import fnmatch
from time import sleep
from subprocess import PIPE, Popen


class ConfigureNginx(object):
    """
    Add files to customize the configuration of nginx and restart the service
    so the changes take effect.

    This agent is Ubuntu 14.04 specific.

    There are 2 types of file that can modify the configuration for nginx:
        - site
        - conf
    Both of these are used as a set of files in the directories:
        - /etc/nginx/sites-enabled
        - /etc/nginx/conf.d
    Respectively.

    We represent the contents of new files for these locations using a pickled
    ASCII argument file. The file contains a dictionary which outlines
    configuration information and locations:
    {
        'sites': {
                    'example': "<file contents>"
                 },
        'conf': {
                   'more_conf.conf': "<file contents>"
                }
    }

    This dictionary would result in the creation of 3 files:
        - /etc/nginx/sites-available/example
        - (symlink) /etc/nginx/sites-enabled/example -> /etc/nginx/sites-available/example
        - /etc/nginx/conf.d/more_conf.conf

    This agent removes the default site from sites-enabled, but leaves the file
    in sites-available for reference.

    IMPORTANT: This agent depends on the presence of a file in /tmp assumed
    to be dropped by the nginx installer. It will sleep and loop forever if the
    file is not present.
    """

    def __init__(self, ascii_file=None, binary_file=None):
        self.ascii_file = ascii_file

    def run(self):
        found = False
        while not found:
            # If the nginx install is not done, then sleep
            # for second and check again
            for fn in os.listdir("/tmp"):
                if fnmatch.fnmatch(fn, "nginx*installed"):
                    # Found that nginx has been installed
                    found = True
                    break
            sleep(1)

        config = None
        with open(self.ascii_file, "r", encoding="utf-8") as f:
            config = pickle.load(f)

        if not config:
            print("Could not load pickled data")
            return

        # Delete the default site
        default_file = "/etc/nginx/sites-enabled/default"
        try:
            os.remove(default_file)
        except Exception as e:
            print("Warning: Unable to remove default site: %s" % e)

        # Handle sites
        if config.get("sites"):
            for site in config["sites"].keys():
                sites_available_dir = os.path.join("/etc", "nginx", "sites-available")
                sites_available = os.path.join(sites_available_dir, site)
                sites_enabled_dir = os.path.join("/etc", "nginx", "sites-enabled")
                sites_enabled = os.path.join(sites_enabled_dir, site)

                # Make sure that needed directories exist
                if not os.path.exists(sites_available_dir):
                    try:
                        os.makedirs(sites_available_dir)
                    except:
                        print("Unable to create directory: %s" % sites_available_dir)

                if not os.path.exists(sites_enabled_dir):
                    try:
                        os.makedirs(sites_enabled_dir)
                    except:
                        print("Unable to create directory: %s" % sites_enabled_dir)

                # Put the file in sites-available with the right permission
                with open(sites_available, "w", encoding="utf-8") as f:
                    f.write(config["sites"][site])

                try:
                    os.chmod(sites_available, int("0644", 8))
                except Exception as e:
                    print("Error: sites_available chmod failed: %s" % e)

                # Link the file to sites-enabled with the correct permissions.
                try:
                    os.symlink(sites_available, sites_enabled)
                except Exception as e:
                    print("Error: Unable to create symlink in sites_enabled: %s" % e)

                try:
                    os.chmod(sites_enabled, int("0644", 8))
                except Exception as e:
                    print("Error: sites_enabled chmod failed: %s" % e)

        # Handle conf
        if config.get("conf"):
            for conf in config["conf"].keys():
                conf_path = os.path.join("/etc", "nginx", "conf.d", conf)

                with open(conf_path, "w", encoding="utf-8") as f:
                    f.write(config["conf"][conf])

        # Restart the service
        restart = Popen(["service", "nginx", "restart"], stdout=PIPE, stderr=PIPE)
        output = restart.communicate()
        if restart.returncode != 0:
            print("Unable to restart nginx service")
            print(output[1])


if __name__ == "__main__":
    # Only takes an ascii file
    configure = ConfigureNginx(sys.argv[1])
    configure.run()
