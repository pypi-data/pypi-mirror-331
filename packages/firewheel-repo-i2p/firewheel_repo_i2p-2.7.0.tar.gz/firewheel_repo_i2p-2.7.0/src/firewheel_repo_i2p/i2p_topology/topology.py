import random
from array import *

import netaddr
from base_objects import Switch
from dns.dns_objects import DNSServer
from i2p.i2p_objects import (
    CC,
    BTTracker,
    I2PRouter,
    I2PBootstrapServer,
    set_ubuntu_version,
)
from ntp.time_server import NTPServer
from generic_vm_objects import GenericRouter

from firewheel.control.experiment_graph import Vertex, AbstractPlugin

# Begin topology generation function definitions #########

# Distribution A (distA) is the histogram profile of the number
# of /16s with x number of i2p Routers.
# Reference: Figure 14 in P. Liu, et al., "Empirical Measurments
#            and Analysis of I2P Routers", Journal of Networks,
#            Vol. 9, No. 9, September 2014.
distA = array("i", [0, 2500, 600, 200, 100, 50, 20, 10, 5, 2, 1, 1, 1, 1, 1])

# Distribution B (distB) is the histogram profile of the number
# of BGP Routers (Level 2 in our topology) with y number of /16s
# Reference: This histogram of the number of BGP ASs with a given
#            number of equivalent /16s was derived from the CAIDA
#            files in the /opt/firewheel/model_components/i2p/data
#            caida directory. The file used in that directory was
#            routeviews-rv2-201502.gz. This histogram had an entry
#            supporting over 1500 equivalent /16s, but this seemed
#            to be an anomaly. So the histogram was truncated here
#            at 200 /16 equivalents maximum.
# fmt: off
distB = array('i',[0, 1797, 362, 172, 124, 73, 42, 45, 34, 21, 29,
                    15, 21, 11, 18, 10, 21, 13, 4, 12, 9,
                    6, 8, 12, 4, 8, 7, 8, 2, 8, 3,
                    1, 6, 4, 4, 4, 6, 0, 4, 7, 0,
                    5, 1, 3, 1, 1, 5, 4, 3, 1, 1,
                    3, 4, 1, 2, 3, 1, 0, 0, 1, 1,
                    0, 1, 0, 2, 2, 0, 2, 1, 2, 2,
                    0, 1, 1, 1, 2, 1, 1, 0, 0, 5,
                    1, 2, 3, 1, 1, 1, 0, 0, 0, 1,
                    0, 1, 2, 3, 0, 1, 0, 2, 1, 2,
                    0, 2, 0, 0, 2, 0, 0, 1, 0, 1,
                    1, 1, 0, 2, 0, 1, 0, 0, 0, 2,
                    0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
                    0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                    1, 1, 1, 2, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                    0, 0, 0, 1, 2, 0, 1, 0, 0, 0])
# fmt: on


def initialize(an_array):
    """
    Build the cumulative distribution function from the given histogram array.

    Args:
        an_array (list): A histogram array from which to build the CDF.

    Returns:
        array: A cumulative distribution function represented as an array.
    """
    dsum = float(sum(an_array))
    new_array = array("d", [0])
    for n in range(1, len(an_array)):
        x = float(an_array[n]) / dsum + new_array[n - 1]
        new_array.append(x)
    return new_array


def init_number16s():
    """
    Initialize the I2P number space to begin at a specified value.

    Returns:
        int: The initial state for the I2P number space.
    """
    # We want to initialize at 11.0.0.0
    state = 184549376  # int('00001011000000000000000000000000',2)
    return state


def number16s(state, an_array):
    """
    Generate the number of /16s a BGP router is to support.
    Specifically useful to return the number of /16s per lowest tier BGP routers
    which support the I2P routers.

    Args:
        state (int): The current state of the I2P number space.
        an_array (list): A cumulative distribution function array.

    Returns:
        tuple: A tuple containing the updated state, the number of /16s,
               and the associated IP address and mask.
    """

    # These address blocks are to be avoided, i.e., jumped over
    # int('10101100000100000000000000000000',2) = 2886729728 which is 172.16.0.0
    # int('10101100000011111111111111111111',2) = 2886729727 which is 172.31.255.255
    #
    # int('11000000101010000000000000000000',2) = 3232235520 which is 172.16.0.0
    # int('11000000101010001111111111111111',2) = 3232301055 which is 172.16.0.0

    excludedState1 = 2886729728
    skipState1 = 2886729727
    excludedState2 = 3232235520
    skipState2 = 3232301055

    ipAddressMask = 16

    # Sample over the previous CDF
    r = random.random()
    n = 0
    while an_array[n] < r:
        n += 1
    number16s = n
    number16s = min(number16s, 128)
    #    if number16s > 32: number16s = 32

    # Determine the associated mask based upon the above number16s
    n = 0
    max = 1
    # n = 1; max = 1
    while max < number16s:
        max *= 2
        n += 1
    ipAddressMask -= n

    # Find the next /ipAddressMask - orig
    # state = ((state>>(32-ipAddressMask))+1)<<(32-ipAddressMask)
    # ipAddress = state
    # state = ((state>>(32-ipAddressMask))+1)<<(32-ipAddressMask)
    # ipAddressAndMask = str(netaddr.IPAddress(ipAddress)) + '/' + str(ipAddressMask)
    # print 'number16s = ', number16s, 'IP Address Space = ', ipAddressAndMask, 'IP addr = ', ipAddress

    # Find the next /ipAddressMask - new
    nextState = ((state >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)
    ipAddress = nextState
    nextState = ((nextState >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)
    if excludedState2 > state and excludedState2 < nextState:
        state = skipState2 + 1
        nextState = ((state >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)
        ipAddress = nextState
        nextState = ((nextState >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)
    elif excludedState1 > state and excludedState1 < nextState:
        state = skipState1 + 1
        nextState = ((state >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)
        ipAddress = nextState
        nextState = ((nextState >> (32 - ipAddressMask)) + 1) << (32 - ipAddressMask)

    ipAddressAndMask = str(netaddr.IPAddress(ipAddress)) + "/" + str(ipAddressMask)
    state = nextState

    return state, number16s, ipAddressAndMask


def numberI2ps(an_array):
    """
    Generate the number of I2P routers in an instance of /16.

    Args:
        an_array (list): A cumulative distribution function array.

    Returns:
        int: The number of I2P routers in the specified /16.
    """
    # Sample over the given CDF
    r = random.random()
    n = 0
    while an_array[n] < r:
        n += 1
    number = n

    return number


def get_num_bgp_and_seed(target, initial_seed=0, threshold=0.025, logger=None):
    """
    Calculate the number of BGP routers needed to support a specified number of I2P routers.

    Args:
        target (int): The target number of I2P routers.
        initial_seed (int, optional): The initial seed for random number generation.
        threshold (float, optional): The threshold for the number of I2P routers.
        logger (Logger, optional): A logger instance for logging information.

    Returns:
        dict: A dictionary containing the seed, number of BGP routers, total I2P routers,
              and the topology.
    """
    if logger:
        logger.info(
            "get_num_bgp_and_seed: Calculating the Number of BGP Routers to use for %s total i2p Routers."
            % (str(target),)
        )
    seed = initial_seed
    cdfDistA = initialize(distA)
    cdfDistB = initialize(distB)
    success = False
    while not success:
        random.seed(seed)
        randomstate = random.getstate()
        state = init_number16s()
        total_numberI2pRouters = 0
        num_bgps = 0
        topology = []
        while total_numberI2pRouters <= (1 - threshold) * target:
            num_bgps += 1
            state, numberSixteens, addressAndMask = number16s(state, cdfDistB)
            numI2ps = []
            for k in range(numberSixteens):
                numberI2pRouters = numberI2ps(cdfDistA)
                numI2ps.append(numberI2pRouters)
                total_numberI2pRouters += numberI2pRouters
            topology.append(
                {
                    "num16s": numberSixteens,
                    "addr&Mask": addressAndMask,
                    "numI2pPer16": numI2ps,
                }
            )
        success = (total_numberI2pRouters >= (1 - threshold) * target) and (
            total_numberI2pRouters <= (threshold + 1) * target
        )

        if success:
            # random.seed(seed)
            random.setstate(randomstate)
            ret = {
                "seed": seed,
                "Tier_2_BGPs": num_bgps,
                "i2p_Routers": total_numberI2pRouters,
                "Topology": topology,
            }
            if logger:
                for k, v in ret.items():
                    logger.info("get_num_bgp_and_seed: {}={}".format(k, v))
            # print("\n".join("{}={}".format(k,v) for k,v in ret.items()))
            return ret
        else:
            seed += 1


# def get_seed_only(target, num_bgps, initial_seed=0, threshold=.025, logger=None):
#    if logger:
#        logger.info("get_seed_only: Calculating the Number of BGP Routers to use for %s total i2p Routers." % (str(target),))
#    seed = initial_seed
#    cdfDistA = initialize( distA )
#    cdfDistB = initialize( distB )
#    success = False
#    while not success:
#        random.seed(seed)
#        randomstate = random.getstate()
#        state = init_number16s()
#        total_numberI2pRouters = 0
#        #num_bgps = 0
#        #while total_numberI2pRouters <= (1-threshold) * target:
#        for j in range(num_bgps):
#            state, numberSixteens, addressAndMask = number16s( state, cdfDistB )
#            num_i2ps_in_bgp = 0
#            for k in range(numberSixteens):
#                numberI2pRouters = numberI2ps( cdfDistA )
#                num_i2ps_in_bgp += numberI2pRouters
#                total_numberI2pRouters += numberI2pRouters
#            # we don't want more than 128 i2p routers per tier2 bgp
#            if num_i2ps_in_bgp > 128:
#                total_numberI2pRouters = 0
#                break
#        success = ((total_numberI2pRouters >= (1 - threshold) * target) and (total_numberI2pRouters <= (threshold + 1) * target))
#        if success:
#            #random.seed(seed)
#            random.setstate(randomstate)
#            ret = {"seed" : seed, "Tier_2_BGPs" : num_bgps, "i2p_Routers" : total_numberI2pRouters}
#            if logger:
#                for k,v in ret.items():
#                    logger.info("get_seed_only: {}={}".format(k,v))
#            return ret
#        else:
#            seed += 1

# Ends function definitions #############################


class Topology(AbstractPlugin):
    """
    This class creates a variable-sized Invisible Internet Project (I2P)
    overlay network topology, including switches, BGP routers, and supporting
    services at the internet and autonomous system (AS) gateway-levels, AS
    internal switches and OSPF routers, hosts within AS subnets for running
    I2P client and server applications.
    """

    def run(
        self,
        num_i2p_routers,
        special_as="0",
        special_num16s="0",
        special_numi2p_per16="0",
        ubuntu_version="14.04",
    ):
        """
        Construct the 'I2P topology' with the given number of routers.

        This is the larger scale, tiered topology model for the I2P studies.
        The topology is built in a structured manner with switches and routers
        connecting various components of the network.

        The topology is built in the following way:

        <switch.internet.net>
                      |          |-- ds.internet.net
                      |          |-- ntp.internet.net
                      |          |-- i2pbootstrap.internet.net
                      |       <switch_dc>
                      |          |
                      |-- BGP router (AS100) -- <switch.as100.net>
                      |                              |
                      |                              | -- BGP router (AS1000001)---<switch.as100001.net>
                      |                              |                                 +--I2P-rtr1.as100001.net
                      |                              |                                 +--I2p-rtr2.as100001.net
                      |                              |                                      ...
                      |                              |
                      |                              | -- BGP router (AS1000002)---<switch.as100002.net>
                      |                              |                                 +--I2P-rtr1.as100002.net
                      |                              |                                 +--I2p-rtr2.as100002.net
                      |                              |                                      ...
                      |
                      |-- BGP router (AS101) -- <switch.as101.net>
                      |                              |
                      |                              | -- BGP router (AS1010001)---<switch.as101001.net>
                      |                              |                                 +--I2P-rtr1.as101001.net
                      |                              |                                 +--I2p-rtr2.as101001.net
                      |                              |                                      ...
                      |                              |
                      |                              | -- BGP router (AS1010002)---<switch.as100002.net>
                      |                              |                                 +--I2P-rtr1.as101002.net
                      |                              |                                 +--I2p-rtr2.as101002.net
                      |                              |                                       ...
                      |        ...
                      |
                      |-- BGP router (AS129) -- <switch.as129.net>
                                                     |
                                                     | -- BGP router (AS1290001)---<switch.as129001.net>
                                                     |                                 +--I2P-rtr1.as129001.net
                                                     |                                 +--I2p-rtr2.as129001.net
                                                     |                                      ...
                                                     |
                                                     | -- BGP router (AS1290002)---<switch.as129002.net>
                                                                                       +--I2P-rtr1.as129002.net
                                                                                       +--I2p-rtr2.as129002.net
                                                                                            ...


        The IP space used for the top tier switches a nd routers is 1.0.0.0/8
        with /22 carved out of it for each BGP router and assoicated AS. The
        first two /22s are used for the Internet switch and the Data Center switch..

        The switches are allocated IP space as follows:
            - Data Center switch has 1.0.4.0/22
            - Internet Tier 1 switch has 1.0.8.0/22
            - Tier 2 switches have (incrementally assigned, starting at) 1.0.12.0/22
            - Tier 3 switches are assigned out of the 11.0.0.0 - 224.0.0.0 space with
              variable masks

        The routers will be named and IP'ed as follows:
            - BGP Tier 1 routers : bgp-rtr.as<n>.net      # 3 digit ASNs
            - BGP Tier 1 routers IF to the Internet Tier 1 switch: 1.0.8.1-30/22
            - BGP Tier 1 routers IF to the Tier 2 switch: 1.0.12+.1/22

            - BGP Tier 2 routers: bgp-rtr.as<n>.net      # 6 digit ASNs (first three
              derived from associated Tier 1 BGP router
            - BGP Tier 2 routers IF to the Internet Tier 2 switch: 1.0.12+.2-m/22
            - BGP Tier 2 routers IF to the Tier 3 switch: 11+.x.0.1/8-16

            - I2P routers: i2p-rtr-<j>.as<n>.net
                  where the addresses are chosen from 11.0.0.0 - 224.0.0.0 address space
                  based upon a estimated distribution of equivalent /16s per Tier 2 AS
                  and the number of I2P routers per /16.
            - I2P routers IF to the Tier 3 switch: 11+.x.0.2+/16

        The servers in AS 100 will be IP'ed as follows:
            - dns.internet.com / 1.0.4.1
            - ntp.internet.com / 1.0.4.2
            - i2prouter.internet.com / 1.0.4.3

        Args:
            num_i2p_routers (int): The approximate number of I2P routers to create.
            special_as (str, optional): Special AS number (default is "0").
            special_num16s (str, optional): Special number of /16s (default is "0").
            special_numi2p_per16 (str, optional): Special number of I2P routers per /16 (default is "0").
            ubuntu_version (str, optional): The version of Ubuntu to use (default is "14.04").

        Raises:
            AssertionError: If the number of I2P routers is not within valid limits (0-3000).
        """

        def get_scheduled_host(v):
            return "any"
            # return v.scheduled_physical_host

        # Parse and sanity check arguments
        #
        num_i2p_routers = int(num_i2p_routers)
        assert num_i2p_routers < 30000
        assert num_i2p_routers > 0

        # Set ubuntu version for all VMs
        set_ubuntu_version(ubuntu_version)

        # Compute remaining topology paraneters
        #
        num_tier1_bgp_routers = 31  # topology assumption
        # only 30 Tier1 will have Tier2, one is data center

        # Note: The 9.9 factor used below is derived from the i2p and /16 distributions defined in
        #       the cdfs/histograms. It represents the mean number of i2p routers per BGP router.
        # num_tier2_bgp_routers = ceil(num_i2p_routers / 9.9)
        # bgp_conf = get_seed_only(target=num_i2p_routers, num_bgps=num_tier2_bgp_routers, initial_seed=0,threshold=.005, logger=self.log)
        #
        # We now find the num_tier2_bgp_routers and randon(seed) values,
        # which will result in producing the total i2p routers we desire.
        bgp_conf = get_num_bgp_and_seed(
            target=num_i2p_routers, initial_seed=0, threshold=0.025, logger=self.log
        )
        num_tier2_bgp_routers = bgp_conf["Tier_2_BGPs"]
        min_num_tier2_per_tier1 = int(
            num_tier2_bgp_routers / (num_tier1_bgp_routers - 1)
        )
        excess_tier2_bgp_routers = num_tier2_bgp_routers % (num_tier1_bgp_routers - 1)
        topology = bgp_conf["Topology"]

        # Initialize device collections
        #
        tier1_bgp_routers = {}
        tier2_switches = {}
        tier2_bgp_routers = {}
        tier2_hosts = {}
        # collection of switch network data
        self.networks = {}

        # Create the IP space for the:
        #   A) Data Center Switch
        #   B) Tier 1 Switch
        #   C) Multiple (e.g. 30) Tier 2 Switches
        #
        one_space_subnets = netaddr.IPNetwork("1.0.0.0/8").subnet(22)

        # Create the Data Center Switch
        #
        dc_ip_space = next(one_space_subnets)
        switch_dc = self.makeSwitch("switch.dc.net", dc_ip_space, "Data Center")

        # Create the Tier 1 (Internet) Switch
        #
        internet_space = next(one_space_subnets)
        switch_tier1 = self.makeSwitch("switch.tier1.net", internet_space, "Tier 1")

        ##########################################################################
        # Create each Tier 1 BGP Router as well as its associated Tier 2 Switch, #
        # and connect the router to both the Tier 1 Switch and its Tier 2 Switch #
        # i.e. forall(x): t1-switch <--> t1-router[x] <--> t2-switch[x]          #
        ##########################################################################

        as_num = "99"
        for _ in range(num_tier1_bgp_routers):
            # Get the next IP space
            ip_space = next(one_space_subnets)

            # Get AS Number
            as_num = str(int(as_num) + 1)

            # Get Domain Suffix
            domain = "as%s.net" % as_num

            # Create Tier 1 Router
            router_tier1 = self.makeRouter("bgp-rtr.%s" % domain, as_num, ip_space)

            # Create Tier 1 Router's Tier 2 Switch -- except for as100, the data center
            if int(as_num) > 100:
                switch_tier2 = self.makeSwitch("switch.%s" % domain, ip_space, "Tier 2")

            # Connect Tier 1 Router to the Tier 1 Switch
            tier1_ip = self.getNextSwitchIP(switch_tier1)
            router_tier1.connect(
                switch_tier1, tier1_ip, self.getSwitchNetmask(switch_tier1)
            )
            self.log.info(
                "Connected Tier 1 ROUTER: %s to Tier 1 %s as %s"
                % (router_tier1.name, switch_tier1.name, tier1_ip)
            )

            # Create Tier 1 Router's Tier 2 Switch, and Connect them
            if int(as_num) > 100:  # except for as100, the data center
                switch_tier2 = self.makeSwitch("switch.%s" % domain, ip_space, "Tier 2")
                tier2_ip = self.getNextSwitchIP(switch_tier2)
                router_tier1.connect(
                    switch_tier2, tier2_ip, self.getSwitchNetmask(switch_tier2)
                )
                self.log.info(
                    "Connected Tier 1 ROUTER: %s to Tier 2 %s as %s"
                    % (router_tier1.name, switch_tier2.name, tier2_ip)
                )

            # Store Tier 1 Router and Tier 2 Switch to their collections for later use
            tier1_bgp_routers[as_num] = router_tier1
            if int(as_num) > 100:  # no tier2 switch in as100, the data center
                tier2_switches[as_num] = switch_tier2

        #######################################################################
        # Link all Tier 1 BGP Routers in a full mesh across the Tier 1 Switch #
        #######################################################################

        tier1_bgp_rtrs_list = sorted(tier1_bgp_routers.values())
        for i in range(len(tier1_bgp_rtrs_list)):
            for j in range(i + 1, len(tier1_bgp_rtrs_list)):
                tier1_bgp_rtrs_list[i].link_bgp(
                    tier1_bgp_rtrs_list[j], switch_tier1, switch_tier1
                )
                self.log.info(
                    "Linked BGP ROUTERS: %s and %s"
                    % (tier1_bgp_rtrs_list[i].name, tier1_bgp_rtrs_list[j].name)
                )

        self.log.info(
            "Total Tier 1 Routers Created = %s"
            % (
                len(
                    tier1_bgp_routers,
                )
            )
        )
        self.log.info(
            "Total Tier 2 Switches Created = %s"
            % (
                len(
                    tier2_switches,
                )
            )
        )

        #####################################
        # Add Data Center Services to AS100 #
        #####################################

        # Get the AS100 Tier 1 Router
        router_dc = tier1_bgp_routers["100"]

        # Connect the AS100 Router to the DC Switch (created above)
        router_dc.connect(
            switch_dc, self.getNextSwitchIP(switch_dc), self.getSwitchNetmask(switch_dc)
        )
        # self.log.info('Connected DATA CENTER ROUTER: %s - %s' %
        #              (router_dc.name, repr(router_dc.routing['ospf']['interfaces'])))

        # Make the DNS Server and connect it to the DC Switch
        server = Vertex(self.g, "dns.internet.net")
        server_ip = self.getNextSwitchIP(switch_dc)
        server.decorate(DNSServer, init_args=[server_ip])
        server = self.config_vm_specs(server, cores=2, mem=2048)
        server.connect(switch_dc, server_ip, self.getSwitchNetmask(switch_dc))
        self.log.info(
            "Created DNS SERVER: %s - IPAddr=%s, Netmask=%s"
            % (server.name, server_ip, self.getSwitchNetmask(switch_dc))
        )

        # Make the NTP Server and connect it to the DC Switch
        server = Vertex(self.g, "ntp.internet.net")
        server_ip = self.getNextSwitchIP(switch_dc)
        server.decorate(NTPServer)
        server = self.config_vm_specs(server, cores=2, mem=2048)
        server.connect(switch_dc, server_ip, self.getSwitchNetmask(switch_dc))
        self.log.info(
            "Created NTP SERVER: %s - IPAddr=%s, Netmask=%s"
            % (server.name, server_ip, self.getSwitchNetmask(switch_dc))
        )

        # Make the i2p Bootstrap Server and connect it to the DC Switch
        server = Vertex(self.g, "i2pbootstrap.internet.net")
        server_ip = self.getNextSwitchIP(switch_dc)
        server.decorate(I2PBootstrapServer)
        server.connect(switch_dc, server_ip, self.getSwitchNetmask(switch_dc))
        self.log.info(
            "Created I2P BOOTSTRAP SERVER: %s - IPAddr=%s, Netmask=%s"
            % (server.name, server_ip, self.getSwitchNetmask(switch_dc))
        )

        # Make the BTTracker Server and connect it to the DC Switch
        server = Vertex(self.g, "superhidden-bttrack.internet.net")
        server_ip = self.getNextSwitchIP(switch_dc)
        server.decorate(BTTracker)
        server.connect(switch_dc, server_ip, self.getSwitchNetmask(switch_dc))
        self.log.info(
            "Created BTTRACKER SERVER: %s - IPAddr=%s, Netmask=%s"
            % (server.name, server_ip, self.getSwitchNetmask(switch_dc))
        )

        # Make the CC Server and connect it to the DC Switch
        server = Vertex(self.g, "cc.internet.net")
        server_ip = self.getNextSwitchIP(switch_dc)
        server.decorate(CC)
        server.connect(switch_dc, server_ip, self.getSwitchNetmask(switch_dc))
        self.log.info(
            "Created CC SERVER: %s - IPAddr=%s, Netmask=%s"
            % (server.name, server_ip, self.getSwitchNetmask(switch_dc))
        )

        # Add the DC Network to the AS100 Router for BGP broadcast
        router_dc.add_bgp_network(dc_ip_space)

        ##########################################################
        # Next, build up the Tier 2 BGP Routers and link them in #
        # a full mesh across their respective Tier 2 Switches    #
        ##########################################################

        extra = 1
        # Iterate through Tier 1 Routers, create and connect the Tier 2 BGP
        # Routers to their Tier 2 Switch, and make full BGP mesh at Tier 2
        tier1_bgp_rtrs_list = sorted(tier1_bgp_routers.values())
        tier1_bgp_rtrs_list = tier1_bgp_rtrs_list[1:]
        for i in range(len(tier1_bgp_rtrs_list)):
            excess_tier2_bgp_routers -= 1
            if excess_tier2_bgp_routers < 0:
                extra = 0
            mesh_these_routers = {}

            # Get the Tier 1 Router, plus its Tier 2 Switch and IP Space
            router_tier1 = tier1_bgp_rtrs_list[i]
            switch_tier2 = tier2_switches[router_tier1.get_bgp_as()]
            ip_space = self.getSwitchNetwork(switch_tier2)

            tier2_as_num = 0
            for j in range(min_num_tier2_per_tier1 + extra):
                # Compute the AS Number for Tier 2 BGP router.
                # Tier 1 BGP routers are assigned 3 digit ASN's starting
                # at 100 and continuing to 130 (roughly).  Tier 2 BGP routers
                # are then assigned 6 digit ASNs with the first three digits
                # inherited from their associated Tier 1 BGP ASN.  The last
                # three digits are assigned incrementally starting at 001.
                tier2_as_num += 1
                as_num = "%s%03d" % (router_tier1.get_bgp_as(), int(tier2_as_num))

                # Get the domain suffix
                domain = "as%s.net" % as_num

                # Create the Tier 2 Routers
                router_tier2 = self.makeRouter("bgp-rtr.%s" % domain, as_num)

                # Connect Tier 2 Router to its Tier 2 Switch
                router_tier2.connect(
                    switch_tier2,
                    self.getNextSwitchIP(switch_tier2),
                    self.getSwitchNetmask(switch_tier2),
                )
                # self.log.info('Connected Tier 2 ROUTER: %s - %s' %
                #              (router_tier2.name, repr(router_tier2.routing['ospf']['interfaces'])))

                # BGP Link the Tier 2 Routers to their Tier 1 Router
                router_tier2.link_bgp(router_tier1, switch_tier2, switch_tier2)
                self.log.info(
                    "Linked BGP ROUTERS: %s and %s"
                    % (router_tier2.name, router_tier1.name)
                )

                # Store Tier 2 Router in its collection for later use
                tier2_bgp_routers[as_num] = router_tier2

                # Add this new router to the temporary mesh set
                mesh_these_routers[as_num] = router_tier2

            ###############################################################################
            # Link these new Tier 2 BGP Routers in a full mesh across their Tier 2 Switch #
            ###############################################################################

            mesh_these_routers_list = list(mesh_these_routers.values())
            for a in range(len(mesh_these_routers_list)):
                for b in range(a + 1, len(mesh_these_routers_list)):
                    mesh_these_routers_list[a].link_bgp(
                        mesh_these_routers_list[b], switch_tier2, switch_tier2
                    )
                    self.log.info(
                        "Linked BGP ROUTERS: %s and %s"
                        % (
                            mesh_these_routers_list[a].name,
                            mesh_these_routers_list[b].name,
                        )
                    )

        self.log.info(
            "Total Tier 2 Routers Created = %s"
            % (
                len(
                    tier2_bgp_routers,
                )
            )
        )

        #################################################################
        # Iterate through the Tier 2 BGP Routers, create and connect a  #
        # Tier 3 Switch for each, create the Host machines for the i2p  #
        # Routers assigned to each Layer 3 Subnet and connect them to   #
        # their Layer 3 Switch;  Also, update each Layer 2 Router's BGP #
        # Network info with the IPNetwork of its related Layer 3 Switch #
        #################################################################

        #        cdfDistA = initialize( distA )
        #        cdfDistB = initialize( distB )
        #        state = init_number16s()

        i2p_routers = {}

        # Iterate over the Tier 2 BGP Routers and:
        #   a) generate the IpAddr and Mask
        #   b) the number of i2p Routers per equivalent /16
        #   c) create Tier 3 Switch and connect Tier 2 BGP Router
        #   d) create Hosts for i2p Routers and connect to Tier 3 Switch
        tier2_bgp_rtrs_list = list(tier2_bgp_routers.values())
        for i in range(len(tier2_bgp_rtrs_list)):
            total_tier2_i2ps = 0
            router_tier2 = tier2_bgp_rtrs_list[i]
            switch_tier3_asn = router_tier2.get_bgp_as()

            #            state, numberSixteens, addressAndMask = number16s( state, cdfDistB )
            #            self.log.info('Adding %s total /16 Networks Under Tier 2 Router %s' % (numberSixteens, router_tier2.name))
            self.log.info(
                "Adding %s total /16 Networks Under Tier 2 Router %s"
                % (topology[i]["num16s"], router_tier2.name)
            )

            # Set the BGP Network the Tier 2 BGP Router will advertise
            #            tier2_network = netaddr.IPNetwork(addressAndMask)
            tier2_network = netaddr.IPNetwork(topology[i]["addr&Mask"])
            router_tier2.add_bgp_network(tier2_network)

            # Get the AS Domain suffix
            domain = "as%s.net" % switch_tier3_asn

            # Create Tier 3 Switch for Tier 2 BGP Router
            switch_tier3 = self.makeSwitch(
                "switch.%s" % domain, tier2_network, "Tier 3"
            )

            # Get the Tier 2 BGP Router's IP Address & Mask for the Tier 3 Subnet
            #            (ipAddr, mask) = addressAndMask.split("/")
            (ipAddr, _mask) = topology[i]["addr&Mask"].split("/")
            ipMask = tier2_network.netmask

            (ip1, ip2, ip3, ip4) = ipAddr.split(".")

            bgp_ip4 = str(int(ip4) + 1)
            bgp_ipAddr = ip1 + "." + ip2 + "." + ip3 + "." + bgp_ip4

            # Connect Tier 2 Router to its Tier 3 Switch
            router_tier2.connect(switch_tier3, bgp_ipAddr, ipMask)
            self.log.info(
                "Assigned IP Address to Tier 2 ROUTER: %s - %s"
                % (bgp_ipAddr, router_tier2.name)
            )

            ######################################################
            # For each /16 allocated for this Tier 3 BGP Router  #
            # sample from distA to get its number of i2p Routers #
            # then create and connect the Hosts for each i2p     #
            # Router to the Tier 3 Switch                        #
            # ####################################################

            new_ip3 = "1"
            i2p_rtr_num = 0
            #            for j in range(numberSixteens):
            for j in range(topology[i]["num16s"]):
                # Calc 2nd octet for this /16
                new_ip2 = str(int(ip2) + j)
                # Calc 3rd octet for this /16
                # new_ip3 = str(int(ip3) + j + 1)

                # Get number of i2p Routers to add to this /16 Network
                #                numberI2pRouters = numberI2ps( cdfDistA )
                numberI2pRouters = topology[i]["numI2pPer16"][j]
                total_tier2_i2ps += numberI2pRouters
                self.log.info(
                    "Adding %s I2P ROUTERS under Tier 2 ROUTER: %s in /16: %s.%s.%s.0"
                    % (numberI2pRouters, router_tier2.name, ip1, new_ip2, new_ip3)
                )
                # self.log.info('Creating %s I2P ROUTERS in /16: %s.%s.%s.0' %
                #                        (numberI2pRouters, ip1, ip2, new_ip3))
                # Create the i2p Routers in this /16 network
                # and connect them all to their Tier 3 Switch
                for k in range(numberI2pRouters):
                    # Derive IP address for this i2p Router
                    new_ip4 = str(int(ip4) + k + 1)  # calc 4th octet
                    newIpAddr = ip1 + "." + new_ip2 + "." + new_ip3 + "." + new_ip4

                    # Create Host for i2p Router
                    i2p_rtr_num += 1
                    i2p_rtr = Vertex(self.g, "i2p-rtr-%s.%s" % (i2p_rtr_num, domain))
                    i2p_rtr.decorate(I2PRouter)

                    # Schedule VM resource for storing the i2p Router's physical host's name at runtime
                    # current_hostname_cb = partial(get_scheduled_host, i2p_rtr)
                    current_hostname_cb = "ignorethis"
                    i2p_rtr.drop_content(
                        -500, "/opt/physical_host.txt", content=current_hostname_cb
                    )

                    # Connect this i2p Router to its Tier 3 Switch
                    # NOTE: Minimum bandwidth rate of 96 kbit (12 KBps) required for i2p to allow Shared Bandwidth.
                    # IMPORTANT: !!! DO NOT SET BANDWIDTH RATE OR RATE_UNIT HERE USING CONNECT(). THEY'LL BE SET LATER ON !!!
                    i2p_rtr.connect(switch_tier3, newIpAddr, ipMask)
                    # i2p_rtr.connect(switch_tier3, newIpAddr, ipMask, rate=320, rate_unit='kbit')
                    # self.log.info('Assigned IP Address to I2P ROUTER: %s - %s' % (newIpAddr, i2p_rtr.name))

                    # Add the i2p Router to its collection for later use
                    i2p_routers[i2p_rtr.name] = i2p_rtr
                    self.log.info(
                        "Added I2P ROUTER: i2p-rtr-%s.%s - IPAddr=%s, Mask=255.255.0.0"
                        % (i2p_rtr_num, domain, newIpAddr)
                    )

            # router_tier2.redistribute_bgp_into_ospf()
            # router_tier2.redistribute_ospf_into_bgp()

            self.log.info(
                "Added %s total i2p Routers to Tier 2 ROUTER: %s"
                % (total_tier2_i2ps, router_tier2.name)
            )

        self.log.info(
            "Total i2p Routers Created = %s"
            % (
                len(
                    i2p_routers,
                )
            )
        )

    def config_vm_specs(
        self, vertex, model="qemu64", sockets=1, cores=1, threads=1, mem=256
    ):
        """
        Configure the virtual machine specifications for a given vertex.

        Args:
            vertex (Vertex): The vertex to configure.
            model (str, optional): The model of the virtual CPU (default is "qemu64").
            sockets (int, optional): The number of CPU sockets (default is 1).
            cores (int, optional): The number of CPU cores per socket (default is 1).
            threads (int, optional): The number of threads per core (default is 1).
            mem (int, optional): The amount of memory in MB (default is 256).

        Returns:
            Vertex: The configured vertex with updated VM specifications.
        """
        # You MUST decorate the Vertex with (at least)
        # VMEndpoint before passing it to this function!!

        # now create and update the 'vm' dictionary on the
        # VMEndpoint object to set some of its properties
        try:
            vertex.vm
        except AttributeError:
            vertex.vm = {}
        vertex.vm["vcpu"] = {
            "model": model,
            "sockets": sockets,
            "cores": cores,
            "threads": threads,
        }
        vertex.vm["mem"] = mem
        return vertex

    def makeSwitch(self, name, network, tier="Network"):
        """
        Create a Switch for use in the topology.

        Args:
            name (str): The name of the switch.
            network (IPNetwork): The switch's IPNetwork.
            tier (str, optional): The switch's tier (level or location) in the
                topology (default is 'Network'). e.g. 'Data Center', 'Tier 1', 'Tier 2', etc.

        Returns:
            Vertex: The created switch vertex.
        """
        switch = Vertex(self.g)
        switch.decorate(Switch, init_args=[name])
        # Store the switch's metadata in the 'networks' collection for later use
        self.networks[name] = [network.cidr, network.iter_hosts()]
        self.log.info(
            "Created %s SWITCH: %s - %s"
            % (tier, name, repr(self.networks[switch.name][0]))
        )
        return switch

    def makeRouter(self, name, asn=None, bgp_net=None, rclass=GenericRouter):
        """
        Create a Router for use in the topology.

        Args:
            name (str): The name of the router.
            asn (int, optional): The router's AS number (default is None).
                Note: A BGP router will need an ASN.
            bgp_net (IPNetwork, optional): The IPNetwork that a BGP router will advertise (default is None).
                Note: A BGP router will need to have this set.
            rclass (type, optional): The class (type) of router to create (default is GenericRouter).
                e.g. Helium115, Helium118, etc. Note: Must be an extension/decorator of VMEndpoint.

        Returns:
            Vertex: The created router vertex.
        """
        router = Vertex(self.g, name)
        router.decorate(rclass)
        router = self.config_vm_specs(router, cores=4, mem=4096)

        # TODO: Determine/set desired Bandwidth - What bandwidth do Helium 1.1.8 Vyos Routers Have?

        if bgp_net:
            # Set the IPNetwork the router will advertise
            router.add_bgp_network(bgp_net)
        if asn:
            # Set the router's AS Number
            router.set_bgp_as(asn)
            # If the router has an AS Number then it's a BGP router
            self.log.info("Created BGP ROUTER: %s" % (name,))
        else:
            self.log.info("Created OSPF ROUTER: %s" % (name,))
        return router

    def getNextSwitchIP(self, switch):
        """
        Get the next available IP from a given switch's IPNetwork's hosts iterator.

        Args:
            switch (Vertex): A reference to the Switch object to get the IP from.

        Returns:
            str: The next available IP address.
        """
        return next(self.networks[switch.name][1])

    def getSwitchNetmask(self, switch):
        """
        Get the netmask of a given switch's IPNetwork.

        Args:
            switch (Vertex): A reference to the Switch object to get the netmask from.

        Returns:
            str: The netmask of the switch's IPNetwork.
        """
        return self.networks[switch.name][0].netmask

    def getSwitchNetwork(self, switch):
        """
        Get the IPNetwork of a given switch.

        Args:
            switch (Vertex): A reference to the Switch object to get the network from.

        Returns:
            IPNetwork: The IPNetwork of the switch.
        """
        return self.networks[switch.name][0]
