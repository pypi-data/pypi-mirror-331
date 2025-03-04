#!/usr/bin/env python
import sys
import json


class ConfigFileAppend(object):
    """
    Agent that will append an arbitrary number of
    parameters to a config file. These parameters are structured as
    KEY=VALUE and appended to the end of the config file.

    ASCII input data structure:

    {
        # Example file to append config parameters for
        <filename> :
        {
            <key> : <value>,
        },
        ...
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

    def run(self):
        """
        Standard agent run function. This performs the work of the agent.
        Requires no parameters, since they are passed into __init__()
        """
        af = open(self.ascii_file, "r", encoding="utf-8")
        config_file = json.loads(af.read())

        # Loop over all passed in dictionaries to write the config parameters
        # to the correct file
        for path in config_file.keys():
            for key in config_file[path]:
                with open(path, "a", encoding="utf-8") as f:
                    f.write(key + "=" + str(config_file[path][key]) + "\n")


if __name__ == "__main__":
    config = ConfigFileAppend(sys.argv[1], sys.argv[2])
    config.run()
