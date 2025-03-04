import json
import random

from i2p.i2p_objects import I2PRouter, BTTrackerGen

from firewheel.control.experiment_graph import AbstractPlugin


class ConfigSnark(AbstractPlugin):
    """
    Intended to append values to the .i2p/router.config file which configures the
    i2p router. Initially written to modify the i2p router bandwidth.

    This assumes that an i2p router vertex is marked with 'is_i2p' = True.
    """

    def run(self, generator_prob="0.20", seeder_prob="0.60", leecher_prob="0.20"):
        """
        Executes the plugin to configure I2P nodes for BitTorrent roles.

        This method determines creators and consumers (not mutually exclusive),
        generates files, publishes to a tracker, and pulls files.

        Args:
            generator_prob (str, optional): Probability of a node being a generator.
            seeder_prob (str, optional): Probability of a node being a seeder.
            leecher_prob (str, optional): Probability of a node being a leecher.
        """
        i2p_list = self.get_i2p_list()
        self.tracker = {
            "tracker_name": "tracktor",
            "website_url": "http://tracktor.i2p",
            "announce_url": "http://tracktor.i2p/announce.php",
        }
        self.set_tracker(i2p_list)

        for i2pnode in i2p_list:
            i2pnode.run_executable(600, "add_tracktor_address.py", None, True)

        # Generate a random sample for all nodes that will run bittorrent.
        generator_prob = float(generator_prob)
        seeder_prob = float(seeder_prob)
        leecher_prob = float(leecher_prob)
        bt_sample = random.sample(
            i2p_list, int(len(i2p_list) * (generator_prob + seeder_prob + leecher_prob))
        )
        random.shuffle(bt_sample)

        gen_len = int(len(i2p_list) * generator_prob)
        seeder_len = int(len(i2p_list) * seeder_prob)
        # print('gen:', list(map(lambda x: x.name, bt_sample[:gen_len])))
        # print('seeder:', list(map(lambda x: x.name, bt_sample[gen_len:gen_len+seeder_len])))

        self.schedule_generators(bt_sample[:gen_len])
        self.schedule_seeders(bt_sample[gen_len : (gen_len + seeder_len)])
        self.schedule_leechers(bt_sample[(gen_len + seeder_len) :])

    def get_i2p_list(self):
        """
        Build a list of all the I2P router vertices in the experiment, except
        for those whose names contain any of the excluded terms ("floodfill").

        Returns:
            list: A list of vertexes, where each vertex is an I2P router available
            for participation in torrenting.
        """
        i2p_list = []
        #        excluded = ['floodfill', 'internet']
        excluded = ["floodfill"]

        vertices = self.g.get_vertices()
        for vertex in vertices:
            if any(ele in vertex.name for ele in excluded):
                continue
            if vertex.is_decorated_by(I2PRouter):
                i2p_list.append(vertex)

        return i2p_list

    def set_tracker(self, i2p_list):
        """
        Set the tracker configuration for the given I2P nodes.

        Args:
            i2p_list (list): A list of I2P router vertices to configure the tracker for.
        """
        CONFIG = {
            "filename": "/home/ubuntu/.i2p/i2psnark.config.d/i2psnark.config",
            "tracker_name": "tracktor",
            "website_url": "http://tracktor.i2p",
            "announce_url": "http://tracktor.i2p/announce.php",
        }
        AGENT_NAME = "i2psnark_set_tracker.py"
        AGENT_TIME = -34

        for i2p in i2p_list:
            i2p.add_vm_resource(AGENT_TIME, AGENT_NAME, json.dumps(CONFIG))

    def schedule_generators(self, i2p_list):
        """
        Schedule generators for a percentage of I2P hosts.

        A generator is defined as a user who both generates content and seeds content.

        Args:
            i2p_list (list): A list of I2P router vertices to schedule as generators.
        """
        excluded = ["internet"]

        for gen in i2p_list:
            # Skip anything already using bittorrent.
            try:
                if "bittorrent_role" in gen["application_data"]["i2p"]:
                    continue
            except KeyError:
                pass
            # Skip anything with name containing anything in excluded list
            if any(ele in gen.name for ele in excluded):
                continue

            # Set up generator
            GEN_FREQ = 600
            GEN_SIZE_MIN = 100 * 1024
            GEN_SIZE_MAX = 25 * 1024 * 1024
            AGENT_TIME = 700
            AGENT_NAME = "i2psnark_generate_torrent.py"

            # Create the config ascii file.
            config = {
                "gen_freq": GEN_FREQ,
                "gen_size_min": GEN_SIZE_MIN,
                "gen_size_max": GEN_SIZE_MAX,
                "tracker_name": self.tracker["tracker_name"],
            }
            gen.add_vm_resource(AGENT_TIME, AGENT_NAME, json.dumps(config))
            # Make sure the node is also a seeder
            self._make_seeder(gen, False)

            # Set our role note.
            if "application_data" not in gen or not gen["application_data"]:
                gen["application_data"] = {}
            if (
                "i2p" not in gen["application_data"]
                or not gen["application_data"]["i2p"]
            ):
                gen["application_data"]["i2p"] = {}
            gen["application_data"]["i2p"]["bittorrent_role"] = "generator"
            gen.name = "generator-" + gen.name

            # Create a generator specific tracker
            gen.decorate(BTTrackerGen)

    def schedule_seeders(self, i2p_list):
        """
        Schedule seeders for a percentage of I2P hosts.

        A seeder is defined as a user who only seeds content and never generates content.

        Args:
            i2p_list (list): A list of I2P router vertices to schedule as seeders.
        """
        excluded = ["internet"]

        for consumer in i2p_list:
            # Skip anything already using bittorrent.
            if (
                "application_data" in consumer
                and consumer["application_data"]
                and "i2p" in consumer["application_data"]
                and consumer["application_data"]["i2p"]
                and "bittorrent_role" in consumer["application_data"]["i2p"]
            ):
                continue
            # Skip anything with name containing anything in excluded list
            if any(ele in consumer.name for ele in excluded):
                continue

            self._make_seeder(consumer)
            consumer.name = "seeder-" + consumer.name

    def _make_seeder(self, consumer, consume=True):
        """
        Helper method to configure a consumer as a seeder.

        Args:
            consumer (Vertex): The I2P router vertex to configure as a seeder.
            consume (bool, optional): Whether to also schedule the consumer.
        """
        # NOW DONE IN configure_bandwidth.py AFTER CONFIGURING VICTIM GROUPS ###############
        #        # Some basic default
        #        config = {}
        #        try:
        #            bw = consumer["guest_data"]["qos"]["rate"]
        #            bw = bw / 8
        #            config['upbw_max'] = bw / 2
        #        except:
        #            raise Exception('BW not found')
        #        consumer.add_vm_resource(-35, 'configure_i2psnark.py', json.dumps(config))
        #############################################################################################
        if consume:
            self._schedule_consumer(consumer, False)
        if "application_data" not in consumer or not consumer["application_data"]:
            consumer["application_data"] = {}
        if (
            "i2p" not in consumer["application_data"]
            or not consumer["application_data"]["i2p"]
        ):
            consumer["application_data"]["i2p"] = {}
        consumer["application_data"]["i2p"]["bittorrent_role"] = "seeder"

    def _schedule_consumer(self, consumer, immediate_delete):
        """
        Schedule the long-lived agent to download torrents.

        Args:
            consumer (Vertex): The I2P router vertex to configure as a consumer.
            immediate_delete (bool): Whether to delete the file immediately after download.
        """
        # Set up consumer
        CONSUME_FREQ = 1200
        TORRENT_LIST_URL = "http://superhidden-bttrack.internet.net:9998/torrentlist"
        AGENT_TIME = 750
        AGENT_NAME = "i2psnark_subscribe_torrent.py"

        # Create the config ascii file.
        config = {
            "consume_freq": CONSUME_FREQ,
            "torrent_list_url": TORRENT_LIST_URL,
            "immediate_delete": immediate_delete,
        }
        consumer.add_vm_resource(AGENT_TIME, AGENT_NAME, json.dumps(config))

        consumer.add_vm_resource(740, "reload_torrents.sh")

    def schedule_leechers(self, i2p_list):
        """
        Schedule leechers for a percentage of I2P hosts.

        Leechers have minimum allowed upload bandwidth and delete the file
        immediately once they've downloaded it.

        Args:
            i2p_list (list): A list of I2P router vertices to schedule as leechers.
        """
        excluded = ["internet"]

        for consumer in i2p_list:
            # Skip anything already using bittorrent.
            if (
                "application_data" in consumer
                and consumer["application_data"]
                and "i2p" in consumer["application_data"]
                and consumer["application_data"]["i2p"]
                and "bittorrent_role" in consumer["application_data"]["i2p"]
            ):
                continue
            # Skip anything with name containing anything in excluded list
            if any(ele in consumer.name for ele in excluded):
                continue

                # NOW DONE IN configure_bandwidth.py AFTER CONFIGURING VICTIM GROUPS ###############
                #            # Configure I2PSnark leechers to have low upload bandwidth.
                #            config = {
                #                'upbw_max': 100 # Minimum is 10.
                #            }
                #            consumer.add_vm_resource(-35, 'configure_i2psnark.py', json.dumps(config))
                #############################################################################################

                # Schedule the torrent downloader.
            self._schedule_consumer(consumer, True)
            if "application_data" not in consumer or not consumer["application_data"]:
                consumer["application_data"] = {}
            if (
                "i2p" not in consumer["application_data"]
                or not consumer["application_data"]["i2p"]
            ):
                consumer["application_data"]["i2p"] = {}
            consumer["application_data"]["i2p"]["bittorrent_role"] = "leecher"
            consumer.name = "leecher-" + consumer.name
