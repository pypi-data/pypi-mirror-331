import json

from i2p.i2p_objects import I2PRouter

from firewheel.control.experiment_graph import AbstractPlugin


class AdvertisedBandwidth(AbstractPlugin):
    """
    Intended to append values to the .i2p/router.config file which configures the
    i2p router. Initially written to modify the i2p router bandwidth.

    This assumes that an i2p router vertex is decorated by the I2PRouter class.
    """

    def run(self, bandwidth=None):
        """
        Executes the plugin.

        This method calls the function to build the list of I2P vertexes and then
        builds the schedule for all nodes.

        Args:
            bandwidth (str, optional): The bandwidth to set. If None, defaults to "DEFAULT".

        Raises:
            AssertionError: If the bandwidth is non-numeric or out of range.
        """
        if bandwidth is None:
            self.bandwidth = "DEFAULT"
        elif bandwidth.isnumeric():
            self.bandwidth = int(bandwidth)
            assert self.bandwidth >= 10
            assert self.bandwidth <= 1000000
        else:
            # error on non-numeric bandwidth value
            assert bandwidth.isnumeric()

        i2p_routers = self._build_i2p_list()
        self._set_advertised_bandwidth(i2p_routers)
        self._set_torrenting_bandwidth(i2p_routers)

    def _build_i2p_list(self):
        """
        Build a list of the I2P vertexes for all hosts in the experiment.

        Returns:
            list: A list of vertexes, where each vertex is an I2P router.
        """
        i2p_list = []

        vertices = self.g.get_vertices()
        for vertex in vertices:
            if vertex.is_decorated_by(I2PRouter):
                i2p_list.append(vertex)

        return i2p_list

    def _set_advertised_bandwidth(self, i2p_list):
        """
        Add the set-advertised-bandwidth agent to the schedule of every I2P router.

        Args:
            i2p_list (list): A list of I2P routers as vertexes.
        """
        vertices = self.g.get_vertices()

        # Set the advertised bandwidth for each i2p node
        agent_name = "set_advertised_bandwidth.py"
        agent_time = -80
        for vertex in i2p_list:
            # Setup the ASCII text structure
            filename = "/home/ubuntu/.i2p/router.config"
            inboundkbps = "i2np.bandwidth.inboundKBytesPerSecond"
            outboundkbps = "i2np.bandwidth.outboundKBytesPerSecond"
            share = "100"
            if (
                "guest_data" in vertex
                and "i2p_share" in vertex["guest_data"]
                and vertex["guest_data"]["i2p_share"] is not None
            ):
                share = vertex["guest_data"]["i2p_share"]
            ascii_text = {
                filename: {
                    "router.sharePercentage": str(share),
                    "i2np.udp.ipv6": "false",
                    "i2np.ntcp.ipv6": "false",
                    "i2np.upnp.enable": "false",
                }
            }

            # Set the advertised bandwidth
            if self.bandwidth == "DEFAULT":
                try:
                    interface = vertex.interfaces.get_interface("eth0")
                    # Interface bandwidth is set in bits/s i.e. kbit, mbit, gbit.
                    if interface["qos"]["rate"] is None:
                        bw = 0
                    else:
                        bw = interface["qos"]["rate"]
                    if bw > 0:
                        # Set default rate_unit if not already set
                        if (
                            "rate_unit" not in interface["qos"]
                            or interface["qos"]["rate_unit"] is None
                            or interface["qos"]["rate_unit"] == ""
                        ):
                            interface["qos"]["rate_unit"] = "mbit"  # the default
                        # Convert bw to kbit if needed
                        if interface["qos"]["rate_unit"] == "mbit":
                            bw *= 1000
                        elif interface["qos"]["rate_unit"] == "gbit":
                            bw *= 1000000
                        # Since i2p bandwidth is set in bytes/s (KBps) we need to divide
                        # the interface kbit rate by 8 to convert to KBps, and also ensure
                        # a 5 KBps minimum (the min advertised outbound KBps i2p allows).
                        bw = max(int(bw / 8), 5)
                    else:
                        # If interface qos rate not set, then check if qos set in vertex
                        bw = vertex["guest_data"]["qos"]["rate"]
                        if bw > 0:
                            # Set default rate_unit if not already set
                            if (
                                "rate_unit" not in vertex["guest_data"]["qos"]
                                or vertex["guest_data"]["qos"]["rate_unit"] is None
                                or vertex["guest_data"]["qos"]["rate_unit"] == ""
                            ):
                                vertex["guest_data"]["qos"]["rate_unit"] = (
                                    "mbit"  # the default
                                )
                            # Convert bw to kbit if needed
                            if vertex["guest_data"]["qos"]["rate_unit"] == "mbit":
                                bw *= 1000
                            if vertex["guest_data"]["qos"]["rate_unit"] == "gbit":
                                bw *= 1000000
                            # Since i2p bandwidth is set in bytes/s (KBps) we need to divide
                            # the interface kbit rate by 8 to convert to KBps, and also ensure
                            # a 5 KBps minimum (the min advertised outbound KBps i2p allows).
                            bw = max(int(bw / 8), 5)
                        else:
                            # If interface qos rate not set, and vertex qos rate not set, then set bw to 16384
                            # (the max advertised outbound KBps i2p allows - because if the interface's
                            #  bw rate isn't set it will default to the host network's maximum capacity)
                            bw = 16384
                except:
                    # If interface 'eth0' not found, and vertex qos rate not set, then set bw to 16384
                    # (the max advertised outbound KBps i2p allows - because I have no idea what up with that)
                    bw = 16384
            else:
                # must be KBps if passed in from firewheel command line
                bw = self.bandwidth

            # Ensure 16384 KBps maximum (the max advertised outbound KBps i2p allows)
            bw = min(bw, 16384)

            # Set bw values to use when configuring i2p router's advertised bandwidth
            ascii_text[filename][inboundkbps] = (
                bw * 2
            )  # Multiply outbound KBps by 2 to derive inbound KBps, though i2p
            # multiplies by 5 for its default advertised inbound KBps rate.
            ascii_text[filename][outboundkbps] = bw
            jsond_ascii = json.dumps(ascii_text)
            vertex.add_vm_resource(agent_time, agent_name, jsond_ascii, None)

            ##############################################################
            # NOTE: This is how to change Java JVM Max Memory -Xmx setting
            #
            # IMPORTANT: Reenable if using multiple_clients!!!
            # TODO: Move this to somewhere in multiple_clients, or to
            #       config floodfills MC
            #
            # FOR NOW NOTE: Set only for floodfills
            ##############################################################
            if "floodfill" in vertex.name:
                at = {"/etc/i2p/wrapper.config": {"wrapper.java.maxmemory": "1100"}}
                vertex.run_executable(-41, "remove_old_maxmemory.sh", None)
                vertex.add_vm_resource(-40, agent_name, json.dumps(at), None)
            ##############################################################

            # Save the advertised bandwidth into application_data. Used below to set torrenting bandwidth.
            if "application_data" not in vertex or not vertex["application_data"]:
                vertex["application_data"] = {}
            if (
                "i2p" not in vertex["application_data"]
                or not vertex["application_data"]["i2p"]
            ):
                # We set the in-bound bandwidth. Set defaults for share and out-bound.
                vertex["application_data"]["i2p"] = {}
            # Units are believed to be bytes i.e. KBps
            # share_ratio = float(share) / 100.0
            vertex["application_data"]["i2p"]["inboundkbps"] = bw * 2
            vertex["application_data"]["i2p"]["outboundkbps"] = bw
            # vertex['application_data']['i2p']['share_ratio'] = share_ratio

        # Set some nodes to be unreliable I2P participants
        # agent_name = "random_failures.py"
        # agent_time = 200
        # unreliable_vertexes = random.sample(i2p_list, len(i2p_list)/10)
        # for unreliable in unreliable_vertexes:
        #    r1 = random.uniform(10*60, 20*60)
        #    r2 = random.uniform(10*60, 20*60)
        #    failure_settings = {
        #        'mean_lifetime' : r1,
        #        'mean_offtime'  : r2
        #    }
        #    unreliable.add_vm_resource(agent_time, agent_name, json.dumps(failure_settings), None)

    def _set_torrenting_bandwidth(self, i2p_list):
        """
        Add the configure_i2psnark agent to the schedule of every included torrenting router.

        Args:
            i2p_list (list): A list of I2P routers as vertexes.

        Raises:
            Exception: If the bandwidth is not found in the vertex guest data.
        """
        vertices = self.g.get_vertices()

        included = ["seeder", "leecher"]

        for vertex in i2p_list:
            # Process only vertices with name containing a torrenting role specified in included list
            if any(ele in vertex.name for ele in included):
                # Schedule agent to set the Torrenting Upload Bandwidth Max rate
                config = {}
                try:
                    bw = vertex["guest_data"]["qos"]["rate"]
                    bw /= 8  # convert KBits to KBytes
                    config["upbw_max"] = (
                        bw / 2
                    )  # setting to 50% of total - recommended by i2p
                except:
                    raise Exception("BW not found")

                vertex.add_vm_resource(-35, "configure_i2psnark.py", json.dumps(config))
