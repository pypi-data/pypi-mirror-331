import json
import random
import logging

from i2p.i2p_objects import I2PRouter

from firewheel.control.experiment_graph import AbstractPlugin

logging.basicConfig()


FF_BW_SMP = [64, 128, 256, 512, 1024, 2048, 4096]  # BW Rates (in KBytes) to sample from
FF_BW_CNT = [61, 17, 3, 4, 4, 4, 7]  # Pct. (count) of each rate within population
FF_BW_POP = []
for x in range(len(FF_BW_SMP)):
    FF_BW_POP.extend([FF_BW_SMP[x]] * FF_BW_CNT[x])

FF_DEFAULT_FRACTION = 0.06  # 6%, which is what the network will supposedly converge to
FF_MIN_FF = 8  # Select at least this many routers to be floodfills


RTR_BW_SMP = [
    48,
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
]  # BW Rates (in KBytes) to sample from
RTR_BW_CNT = [60, 1, 17, 3, 4, 4, 4, 7]  # Pct. (count) of each rate within population
RTR_BW_POP = []
for x in range(len(RTR_BW_SMP)):
    RTR_BW_POP.extend([RTR_BW_SMP[x]] * RTR_BW_CNT[x])

STARTUP_RATE = 4096
STARTUP_UNIT = "kbit"


class ConfigFloodfills(AbstractPlugin):
    """This plugin configures some I2P routers as floodfill nodes.

    According to the NetDb docs, the network balances to 6% of all nodes
    being Floodfill. These nodes must have >= 128 kbits of share bandwidth
    (which is greater than the default setting).

    This plugin will count the number of eligible I2P routers in the graph,
    select 6% of them to be floodfills, and ensure each has >= FF_MIN_BW of
    shared bandwidth. I2P routers with names containing any excluded terms
    (listed below) are not eligible to be floodfills.
    """

    def run(self, log_folder="", debug="F", fraction=FF_DEFAULT_FRACTION):
        """
        Executes the plugin to configure I2P routers as floodfill nodes.

        This method counts eligible I2P routers, selects a fraction to be
        floodfills, and configures their bandwidth settings.

        Args:
            log_folder (str, optional): The folder where logs will be stored.
            debug (str, optional): The debug level; can be "F" for off, "T" for info, or "D" for debug.
            fraction (float, optional): The fraction of routers to configure as floodfills.

        Raises:
            AssertionError: If the number of floodfill candidates is less than the required number.
        """
        self.log = logging.getLogger("ConfigFloodfills")
        self.log.level = logging.WARNING
        if debug.lower().startswith("t"):
            self.log.level = logging.INFO
        elif debug.lower().startswith("d"):
            self.log.level = logging.DEBUG

        random.seed()
        ff_candidates = []
        # This 'excluded' list assumes we don't want floodfills also having snark torrenting roles
        excluded = ["internet", "generator", "seeder", "leecher"]
        for v in self.g.get_vertices():
            if any(ele in v.name for ele in excluded):
                continue
            if v.is_decorated_by(I2PRouter):
                ff_candidates.append(v)

        num_ff = max(int(FF_DEFAULT_FRACTION * len(ff_candidates)), FF_MIN_FF)
        assert len(ff_candidates) >= num_ff

        # Choose a uniform sample of num_ff routers to make floodfills
        for v in random.sample(ff_candidates, num_ff):
            # schedule the set-floodfill.sh script, it ensures that a floodfill will always be a floodfill
            v.run_executable(-85, "set-floodfill.sh", None, True)

            # update the vertex's name so we can
            # determine later on it's a floodfill
            v.name = "floodfill-" + v.name

            # set memory and vcpu for a floodfill
            v.vm["mem"] = 4096
            v.vm["vcpu"] = {"sockets": 1, "cores": 4, "threads": 1}

            # get the vertex's interface
            interface = v.interfaces.get_interface("eth0")

            # ensure this i2p router has the required vertex metadata fields
            if "qos" not in interface or not interface["qos"]:
                interface["qos"] = {}
            if "rate" not in interface["qos"] or not interface["qos"]["rate"]:
                interface["qos"]["rate"] = None
            if "rate_unit" not in interface["qos"] or not interface["qos"]["rate_unit"]:
                interface["qos"]["rate_unit"] = None

            if interface["qos"]["rate"] is None:
                bw = 0
            else:
                bw = interface["qos"]["rate"]

            if (
                bw > 0
            ):  # a qos rate has previously been set, so minimega will set tc on the edge
                # set default rate_unit if not already set
                if (
                    "rate_unit" not in interface["qos"]
                    or interface["qos"]["rate_unit"] is None
                    or interface["qos"]["rate_unit"] == ""
                ):
                    interface["qos"]["rate_unit"] = "mbit"  # the default

                # convert to kbit if needed
                if interface["qos"]["rate_unit"] == "mbit":
                    bw *= 1000
                elif interface["qos"]["rate_unit"] == "gbit":
                    bw *= 1000000

                # ensure we have enough bandwidth for a floodfill
                if bw < (FF_BW_SMP[0] * 8):
                    interface["qos"]["rate"] = (
                        random.sample(FF_BW_POP, k=1)[0] * 8
                    )  # Sample from dist and convert to kbit
                    interface["qos"]["rate_unit"] = "kbit"

                self.log.debug(
                    "%s is a floodfill, shared bandwidth is %d %s"
                    % (v.name, interface["qos"]["rate"], interface["qos"]["rate_unit"])
                )

            else:  # no qos rate previously set, so we'll set tc on the VM's interface
                self.set_traffic_control(v, STARTUP_RATE, STARTUP_UNIT)

                self.log.debug(
                    "%s is a floodfill, upload bandwidth will be set on VM interface as %d %s, during the startup period."
                    % (v.name, STARTUP_RATE, STARTUP_UNIT)
                )

                # set this floodfill's bandwidth rate
                ff_bw_rate = (
                    random.sample(FF_BW_POP, k=1)[0] * 8
                )  # Sample from dist and convert to kbit
                self.set_traffic_control(v, ff_bw_rate, "kbit", "change")

                self.log.debug(
                    "%s is a floodfill, shared bandwidth will be set on VM interface as %d %s, after the startup period."
                    % (
                        v.name,
                        v["guest_data"]["qos"]["rate"],
                        v["guest_data"]["qos"]["rate_unit"],
                    )
                )

        # Process all non-floodfill i2p routers
        excluded = ["internet", "floodfill"]
        for v in self.g.get_vertices():
            if v.is_decorated_by(I2PRouter):
                # skip all i2p routers in internet datacenter or designated as floodfills
                if any(ele in v.name for ele in excluded):
                    continue

                # schedule the non-floodfill-specific agent
                # NOTE: the set-nofloodfills.sh script ensures that i2p routers will not become floodfills
                v.run_executable(
                    -85, "set-nofloodfill.sh", None, True
                )  # explicitly configure as not floodfill eligible

                # set memory and vcpu for a non-floodfill
                v.vm["mem"] = 2048
                v.vm["vcpu"] = {"sockets": 1, "cores": 1, "threads": 1}

                # get the vertex's interface
                interface = v.interfaces.get_interface("eth0")

                # ensure this i2p router has the required vertex metadata fields
                if "qos" not in interface or not interface["qos"]:
                    interface["qos"] = {}
                if "rate" not in interface["qos"] or not interface["qos"]["rate"]:
                    interface["qos"]["rate"] = None
                if (
                    "rate_unit" not in interface["qos"]
                    or not interface["qos"]["rate_unit"]
                ):
                    interface["qos"]["rate_unit"] = None

                if interface["qos"]["rate"] is None:
                    bw = 0
                else:
                    bw = interface["qos"]["rate"]

                if (
                    bw > 0
                ):  # a qos rate has previously been set, so minimega will set tc on the edge
                    # Set default rate_unit if not already set
                    if (
                        "rate_unit" not in interface["qos"]
                        or interface["qos"]["rate_unit"] is None
                        or interface["qos"]["rate_unit"] == ""
                    ):
                        interface["qos"]["rate_unit"] = "mbit"  # the default

                    # Convert to kbit if needed
                    if interface["qos"]["rate_unit"] == "mbit":
                        bw *= 1000
                    elif interface["qos"]["rate_unit"] == "gbit":
                        bw *= 1000000

                    # ensure we have => minimum default bandwidth for a non-floodfill
                    if bw < (RTR_BW_SMP[0] * 8):
                        interface["qos"]["rate"] = (
                            random.sample(RTR_BW_POP, k=1)[0] * 8
                        )  # Sample from dist and convert to kbit
                        interface["qos"]["rate_unit"] = "kbit"

                    self.log.debug(
                        "%s is a i2p client, shared bandwidth is %d %s"
                        % (
                            v.name,
                            interface["qos"]["rate"],
                            interface["qos"]["rate_unit"],
                        )
                    )

                else:  # no qos rate previously set, so we'll set tc on the VM's interface
                    self.set_traffic_control(v, STARTUP_RATE, STARTUP_UNIT)

                    self.log.debug(
                        "%s is a i2p client, upload bandwidth will be set on VM interface as %d %s, during the startup period."
                        % (v.name, STARTUP_RATE, STARTUP_UNIT)
                    )

                    # set this floodfill's bandwidth rate
                    rtr_bw_rate = (
                        random.sample(RTR_BW_POP, k=1)[0] * 8
                    )  # Sample from dist and convert to kbit
                    self.set_traffic_control(v, rtr_bw_rate, "kbit", "change")

                    self.log.debug(
                        "%s is a i2p client, shared bandwidth will be set on VM interface as %d %s, after the startup period."
                        % (
                            v.name,
                            v["guest_data"]["qos"]["rate"],
                            v["guest_data"]["qos"]["rate_unit"],
                        )
                    )

    def set_traffic_control(self, vertex, rate, rate_unit, cmd="add"):
        """
        Set the traffic control parameters for a given vertex.

        This method schedules an agent that will set the bandwidth rate limit
        on the VM interface during the startup period or after the share/get-netdb
        has completed.

        Args:
            vertex (Vertex): The vertex to configure.
            rate (int): The bandwidth rate to set.
            rate_unit (str): The unit of the rate (e.g., "kbit", "mbit").
            cmd (str, optional): The command type; can be "add" or "change".
        """
        if cmd == "add":
            # schedule agent that will set bandwidth rate limit on VM interface during the startup period of time
            AGENT_TIME = -91

        elif cmd == "change":
            # schedule agent that will set bandwidth rate limit on VM interface after share/get-netdb has completed
            AGENT_TIME = 330

            # store guest VM's post-startup qos rate and rate_unit in vertex for later use e.g. for setting i2p advertised bandwidth
            if "guest_data" not in vertex or not vertex["guest_data"]:
                vertex["guest_data"] = {}
            if "qos" not in vertex["guest_data"] or not vertex["guest_data"]["qos"]:
                vertex["guest_data"]["qos"] = {}

            vertex["guest_data"]["qos"]["rate"] = rate
            vertex["guest_data"]["qos"]["rate_unit"] = rate_unit

        AGENT_NAME = "set_traffic_control.py"
        config = {
            "cmd": cmd,
            "rate": rate,
            "rate_unit": rate_unit,
            "ceil": rate,
            "burst": rate * 2,
            "cburst": rate * 2,
        }
        vertex.add_vm_resource(AGENT_TIME, AGENT_NAME, json.dumps(config))
