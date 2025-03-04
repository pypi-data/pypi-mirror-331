import sys
import json
import random
import logging

from i2p.i2p_objects import I2PRouter

from firewheel.control.experiment_graph import AbstractPlugin

# The default number of victims per group.
# Alternatively, this can be set using the
# 'group_size_num' key in the config file.
GROUP_SIZE = 8

# The default number of sets of each group.
# Alternatively, this can be set using the
# 'num_group_size' key in the config file.
GROUP_SETS = 1


class ConfigVictimGroups(AbstractPlugin):
    def run(self):
        """
        Executes the plugin to configure victim groups for the experiment.

        This method reads victim group configurations from a JSON file,
        sets up the necessary parameters, and configures the I2P routers
        as specified in the configurations.

        Raises:
            SystemExit: If there are issues reading the configuration file,
            or if there are not enough candidate victim VMs for the specified
            number of victim groups.
        """
        self.log = logging.getLogger("ConfigVictimGroups")
        # self.log.level = logging.WARN
        # if debug.lower().startswith('t'):
        #    self.log.level = logging.INFO
        # elif debug.lower().startswith('d'):
        #    self.log.level = logging.DEBUG

        fname = "/opt/firewheel/model_components/i2p/i2p_config_victims/victim_group_configs.json"
        group_cfgs = None

        # Read victim groups' configurations from json file
        try:
            with open(fname, "r", encoding="utf-8") as vgcf:
                group_cfgs = json.load(vgcf)
        except:
            print(
                "\nERROR: Unable to read Victim Group Configurations from file: %s\n"
                % (fname,)
            )
            print("       Aborting Experiment ...\n")
            sys.exit(1)

        # Override default group size num if set in config file
        if "group_size_num" in group_cfgs:
            GROUP_SIZE = group_cfgs["group_size_num"]

        # Override default num group sets if set in config file
        if "num_group_sets" in group_cfgs:
            GROUP_SETS = group_cfgs["num_group_sets"]

        # Skip victim groups configuration if either group size or num sets set to zero
        if GROUP_SIZE == 0 or GROUP_SETS == 0:
            print(
                "\nWARNING: A zero (0) for Victim Group Size/Sets is specified in config file: %s\n"
                % (fname,)
            )
            print("       Skipping the Configuration of Victim Groups ...\n")
            self.add_bw_to_names()
            return

        # Abort experiment if using this MC but no victim group configs specified in config file
        if (
            "victim_groups" not in group_cfgs
            or not group_cfgs["victim_groups"]
            or not isinstance(group_cfgs["victim_groups"], list)
            or group_cfgs["victim_groups"] == []
        ):
            print(
                "\nERROR: No Victim Group Configurations found in file: %s\n" % (fname,)
            )
            print("       Aborting Experiment ...\n")
            sys.exit(1)

        victim_groups = group_cfgs["victim_groups"]

        # separate victim group configs by torrenting role
        seeders = []
        leechers = []
        nosnarks = []

        for vg in victim_groups:
            if vg["torrent"] == "seeder":
                seeders.append(vg)
            elif vg["torrent"] == "leecher":
                leechers.append(vg)
            else:
                nosnarks.append(vg)

        print("\nseeders groups  = %d" % (len(seeders),))
        print("leechers groups = %d" % (len(leechers),))
        print("nosnarks groups = %d" % (len(nosnarks),))
        print("                 ----")
        print(
            "victim groups tot %d\n" % (len(seeders) + len(leechers) + len(nosnarks),)
        )

        # separate candidate victim VMs per torrenting role
        seeder_candidates = []
        leecher_candidates = []
        nosnark_candidates = []

        # this 'excluded' list assumes we don't want floodfills, generators, or datacenter VMs as victims
        excluded = ["floodfill", "generator", "internet"]
        for v in self.g.get_vertices():
            if any(ele in v.name for ele in excluded):
                continue
            if v.is_decorated_by(I2PRouter):
                if "seeder" in v.name:
                    seeder_candidates.append(v)
                elif "leecher" in v.name:
                    leecher_candidates.append(v)
                else:
                    nosnark_candidates.append(v)

        print("\nseeder i2p VMs  = %d" % (len(seeder_candidates),))
        print("leecher i2p VMs = %d" % (len(leecher_candidates),))
        print("nosnark i2p VMs = %d" % (len(nosnark_candidates),))
        print("                 ----")
        print(
            "VM candidates tot %d\n"
            % (
                len(seeder_candidates)
                + len(leecher_candidates)
                + len(nosnark_candidates),
            )
        )

        print(
            "\ngroup size = %d    tot sets of groups = %d\n" % (GROUP_SIZE, GROUP_SETS)
        )

        seeders_needed = len(seeders) * GROUP_SIZE * GROUP_SETS
        leechers_needed = len(leechers) * GROUP_SIZE * GROUP_SETS
        nosnarks_needed = len(nosnarks) * GROUP_SIZE * GROUP_SETS

        print("\ntot seeders needed  = %d" % (seeders_needed,))
        print("tot leechers needed = %d" % (leechers_needed,))
        print("tot nosnark needed  = %d" % (nosnarks_needed,))
        print("                     -----")
        print(
            "total victims needed  %d\n"
            % (seeders_needed + leechers_needed + nosnarks_needed,)
        )

        if (
            len(seeder_candidates) < seeders_needed
            or len(leecher_candidates) < leechers_needed
            or len(nosnark_candidates) < nosnarks_needed
        ):
            print(
                "\nERROR: Not enough Candidate Victim VMs for the specified number of Victim Groups!\n"
            )
            print(
                "              Seeder Victim Groups: %d    Seeder VMs Needed: %d   Available: %d"
                % (len(seeders), seeders_needed, len(seeder_candidates))
            )
            print(
                "             Leecher Victim Groups: %d   Leecher VMs Needed: %d   Available: %d"
                % (len(leechers), leechers_needed, len(leecher_candidates))
            )
            print(
                "             NoSnark Victim Groups: %d   NoSnark VMs Needed: %d   Available: %d\n"
                % (len(nosnarks), nosnarks_needed, len(nosnark_candidates))
            )
            print("       Aborting Experiment ...\n")
            sys.exit(1)

        # init random
        random.seed()

        # Configure Seeder Victim Groups
        self.configure_victims(
            seeders,
            seeder_candidates,
            seeders_needed,
            snark_role="S",
            passes=GROUP_SETS,
        )

        # Configure Leecher Victim Groups
        self.configure_victims(
            leechers,
            leecher_candidates,
            leechers_needed,
            snark_role="L",
            passes=GROUP_SETS,
        )

        # Configure NoSnark Victim Groups
        self.configure_victims(
            nosnarks,
            nosnark_candidates,
            nosnarks_needed,
            snark_role="N",
            passes=GROUP_SETS,
        )

        print("\nLooking good!!!\n")

    def configure_victims(
        self, victim_groups, victim_candidates, victims_needed, snark_role="", passes=1
    ):
        """
        Configure the specified victim groups with the given candidates.

        This method assigns the necessary configurations to the victim
        routers based on the provided victim groups and their required
        parameters.

        Args:
            victim_groups (list): The list of victim group configurations.
            victim_candidates (list): The list of candidate I2P routers.
            victims_needed (int): The number of victims to configure.
            snark_role (str, optional): The role of the snark (e.g., "S", "L", "N").
            passes (int, optional): The number of passes to configure.
        """
        if victim_groups == [] or victims_needed == 0:
            return

        grp_num = 0
        grp_conf = victim_groups[grp_num]
        vic_num = 0
        pass_num = 0

        # Choose a uniform sample of (size = victims_needed) i2p routers to configure into victim groups
        for v in random.sample(victim_candidates, victims_needed):
            # Configure current vertex 'v' with its current victim group's configuration settings

            # update the vertex's name so we can determine its victim group later on
            num_tunnels_cd = "M" if grp_conf["num_tunnels"] == "max" else "D"
            len_tunnels_cd = "M" if grp_conf["len_tunnels"] == "max" else "D"
            grp_id = (
                "vg"
                + "{:02d}".format(grp_conf["cpu_cores"])
                + "{:03d}".format(grp_conf["bw_rate"])
                + "{:03d}".format(grp_conf["i2p_share"])
                + "{}{}".format(num_tunnels_cd, len_tunnels_cd)
                + snark_role
            )
            v.name = grp_id + "-" + str(pass_num) + "." + v.name

            # update the vertex's vcpu with the victim group's cpu_cores configuration
            v.vm["vcpu"] = {
                "sockets": 1,
                "cores": int(grp_conf["cpu_cores"]),
                "threads": 1,
            }

            # schedule a tc commands to set the vertex's bandwidth with the victim group's bw_rate configuration
            # and set the vertex's guest_data rate and rate_unit to this bw_rate configuration too
            # Note: bw_rate is specified in kB/s, so we multiply it by 8 to convert to kbit
            self.set_traffic_control(v, int(grp_conf["bw_rate"]) * 8, "kbit")

            # update the vertex's guest_data i2p_share with the victim group's i2p_share configuration
            v["guest_data"]["i2p_share"] = int(grp_conf["i2p_share"])

            if grp_conf["num_tunnels"] != "def" or grp_conf["len_tunnels"] != "def":
                # schedule agent(s) to configure client tunnel settings
                self.config_i2p_tunnels(
                    v, grp_conf["num_tunnels"], grp_conf["len_tunnels"]
                )

            print(
                "Configured VM name: %s\t\tcores: %d\trate: %d kB/s\tshare: %d\ttunnelQty: %s\ttunnelLen: %s "
                % (
                    v.name,
                    v.vm["vcpu"]["cores"],
                    v["guest_data"]["qos"]["rate"] / 8,
                    v["guest_data"]["i2p_share"],
                    grp_conf["num_tunnels"],
                    grp_conf["len_tunnels"],
                )
            )

            vic_num += 1
            if vic_num == GROUP_SIZE:
                grp_num += 1
                if grp_num == len(victim_groups):
                    pass_num += 1
                    if pass_num == passes:
                        break
                    else:
                        grp_num = 0
                grp_conf = victim_groups[grp_num]
                vic_num = 0

    def set_traffic_control(self, vertex, rate, rate_unit):
        """
        Set the traffic control parameters for a given vertex.

        This method schedules an agent that will set the bandwidth rate limit
        on the VM interface after the original baseline rate has been set.

        Args:
            vertex (Vertex): The vertex to configure.
            rate (int): The bandwidth rate to set.
            rate_unit (str): The unit of the rate (e.g., "kbit").
        """
        # schedule agent that will set bandwidth rate limit on VM interface after original baseline rate has been set @TIME=330
        AGENT_TIME = 360

        # store guest VM's post-startup qos rate and rate_unit in vertex for later use e.g. for setting i2p advertised bandwidth
        if "guest_data" not in vertex or not vertex["guest_data"]:
            vertex["guest_data"] = {}
        if "qos" not in vertex["guest_data"] or not vertex["guest_data"]["qos"]:
            vertex["guest_data"]["qos"] = {}

        vertex["guest_data"]["qos"]["rate"] = rate
        vertex["guest_data"]["qos"]["rate_unit"] = rate_unit

        AGENT_NAME = "set_traffic_control.py"
        # run tc replace commands since
        config = {
            "cmd": "change",
            "rate": rate,
            "rate_unit": rate_unit,
            "ceil": rate,
            "burst": rate * 2,
            "cburst": rate * 2,
        }
        vertex.add_vm_resource(AGENT_TIME, AGENT_NAME, json.dumps(config))

        # finally, clear any qos data previously set to be applied by minimega to the edge
        interface = vertex.interfaces.get_interface("eth0")
        if (
            "qos" in interface
            and interface["qos"]
            and "rate" in interface["qos"]
            and interface["qos"]["rate"]
        ):
            interface["qos"]["rate"] = None
            if "rate_unit" in interface["qos"] and interface["qos"]["rate_unit"]:
                interface["qos"]["rate_unit"] = None

    def config_i2p_tunnels(self, vertex, num_tunnels, len_tunnels):
        """
        Configure the I2P tunnels for a given vertex.

        This method schedules agents to set the number and length of the
        tunnels based on the provided parameters.

        Args:
            vertex (Vertex): The vertex to configure.
            num_tunnels (str): The number of tunnels to configure.
            len_tunnels (str): The length of the tunnels to configure.
        """
        AGENT_TIME = 1

        if num_tunnels == "max":
            # schedule agent to configure client tunnels Length=4
            AGENT_TIME = -29
            AGENT_NAME = "config-i2p-maxtunnels.sh"
            vertex.run_executable(AGENT_TIME, AGENT_NAME, None, True)

        if len_tunnels == "max":
            # schedule agent to configure client tunnels LengthVariance=2
            AGENT_TIME = -28
            AGENT_NAME = "config-i2p-longtunnels.sh"
            vertex.run_executable(AGENT_TIME, AGENT_NAME, None, True)

        if AGENT_TIME < 0:
            # schedule agent to reload i2p configuration files
            AGENT_TIME = -27
            AGENT_NAME = "config-i2p-reload.sh"
            vertex.run_executable(AGENT_TIME, AGENT_NAME, None, True)

    def add_bw_to_names(self):
        """
        Prepend bandwidth rates to the names of I2P routers.

        This method modifies the names of the I2P routers to include their
        configured bandwidth rates and units.
        """
        print("   Prepending Bandwidth Rates to i2p hostnames instead ...\n")

        for vertex in self.g.get_vertices():
            if vertex.is_decorated_by(I2PRouter):
                if "internet" in vertex.name:
                    continue
                # don't forget to convert kbits to kBytes, by dividing rate by 8, before adding to hostname
                vertex.name = (
                    str(int(vertex["guest_data"]["qos"]["rate"] / 8))
                    + vertex["guest_data"]["qos"]["rate_unit"][0]
                    + "_"
                    + vertex.name
                )
