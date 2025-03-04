import json
import random

from linux.ubuntu import UbuntuServer, UbuntuDesktop
from linux.ubuntu1404 import Ubuntu1404Server, Ubuntu1404Desktop
from linux.ubuntu1604 import Ubuntu1604Server, Ubuntu1604Desktop

from firewheel.control.experiment_graph import require_class

ubuntu_version = "14.04"


def set_ubuntu_version(version):
    """
    Set the global Ubuntu version.

    Args:
        version (str): The version of Ubuntu to set.
    """
    global ubuntu_version
    ubuntu_version = version


@require_class(UbuntuDesktop)
class I2PRouter(object):
    def __init__(self):
        """
        Initialize the I2P Router.

        This constructor sets up the I2P router based on the specified
        Ubuntu version, installs necessary packages, and configures
        the router settings, including Firefox proxy settings and
        netDB sharing.
        """
        if ubuntu_version in {"16", "16.04"}:
            self.decorate(Ubuntu1604Desktop)
            # Install i2p router software from debian files
            self.install_debs(-100, "i2p_0.9.47x-2~xenial+1_debs.tgz")
        else:
            self.decorate(Ubuntu1404Desktop)
            # Install i2p router software from debian files
            self.install_debs(-100, "i2p-0.9.45-trusty-desktop.tgz")

        random.seed()

        # Enable passwordless ssh/scp
        self.add_default_profiles()

        # Configure Firefox to use the Proxy
        self.drop_file(-102, "/home/ubuntu/mozilla-profile.tgz", "mozilla-profile.tgz")
        self.run_executable(
            -101, "tar", "-C /home/ubuntu -xf /home/ubuntu/mozilla-profile.tgz"
        )
        self.run_executable(-100, "chown", "-R ubuntu:ubuntu /home/ubuntu/.mozilla")
        self.run_executable(-100, "rm", "-f /home/ubuntu/mozilla-profile.tgz")

        # Share the netDB
        self.run_executable(random.randint(-99, -90), "share-netdb.sh", None, True)

        # Pull down the full netDbs
        self.run_executable(random.randint(5, 25), "get-netdb.sh", None, True)

        # Configure i2p router
        self.run_executable(-89, "config-i2p-router.sh", None, True)

        # Configure i2p router logger
        self.run_executable(-89, "config-i2p-logger.sh", None, True)

        # Add agents for monitoring statistics
        # self.run_executable(60, 'summaryframe.py', None, True)
        # self.run_executable(61, 'tunnels.py', None, True)

        # Add an agent to perform background traffic
        # Note: enable if you want, typically snark is used instead
        # self.run_executable(random.randint(660,1260), 'background_traffic.sh', None, True)

        self.vm["mem"] = 2048
        self.vm["vcpu"] = {"sockets": 1, "cores": 4, "threads": 1}


@require_class(UbuntuServer)
class I2PBootstrapServer(object):
    def __init__(self):
        """
        Initialize the I2P Bootstrap Server.

        This constructor sets up the I2P bootstrap server based on the
        specified Ubuntu version and configures the server settings.
        """
        if ubuntu_version in {"16", "16.04"}:
            self.decorate(Ubuntu1604Server)
        else:
            self.decorate(Ubuntu1404Server)

        # Bump up the memory & cpu cores
        self.vm["mem"] = 4096
        self.vm["vcpu"] = {"sockets": 1, "cores": 4, "threads": 1}

        # Enable passwordless ssh/scp
        self.add_default_profiles()

        # Run the i2p bootstrap web server
        self.run_executable(1, "i2p_bootstrap_webserver.sh", None, True)


@require_class(I2PRouter)
class CC(object):
    def __init__(self):
        """
        Initialize the CC (Content Creator) class.

        This constructor creates a tunnel for the content creator and
        sets up the necessary configurations for sharing the tunnel's
        base32 address and starting the content creator server.
        """
        # Create the tunnel -- RUNS IN POSITIVE TIME
        json_config = json.dumps(
            {
                "name": "c0ers10n",
                "website_name": "c0ers10n.i2p",
                "port": "9999",
                "number_of_tunnels": "3",
            }
        )
        self.add_vm_resource(100, "i2p_create_tunnel.py", json_config)

        # Share the tunnel's base32 address
        self.run_executable(120, "share_cc_base32_addr.sh", None, True)

        # Add in the torrenttz server setup
        self.run_executable(-65, "start_cc.sh", None, True)


@require_class(I2PRouter)
class BTTracker(object):
    def __init__(self):
        """
        Initialize the BTTracker class.

        This constructor sets up the OpenTracker for BitTorrent and
        configures the necessary settings for the tracker server.
        """
        self.vm["mem"] = 10240
        self.vm["vcpu"] = {"sockets": 1, "cores": 8, "threads": 1}

        # Install OpenTracker (i2p version)
        self.install_debs(-75, "i2p-opentracker-trusty-server.tgz")

        # Install mktorrent
        self.install_debs(-74, "mktorrent-trusty-server.tgz")

        # Create the OpenTracker tunnel -- RUNS IN POSITIVE TIME
        json_config = json.dumps(
            {
                "name": "tracktor",
                "website_name": "tracktor.i2p",
                "port": "6969",
                "number_of_tunnels": "5",
            }
        )
        self.add_vm_resource(100, "i2p_create_tunnel.py", json_config)

        # Add in the torrenttz server setup
        self.run_executable(-65, "make_torrentzz_server.sh", None, True)

        self.run_executable(1, "i2p-opentracker-setup.sh", None, True)


@require_class(I2PRouter)
class BTTrackerGen(object):
    def __init__(self):
        """
        Initialize the BTTrackerGen class.

        This constructor sets up the OpenTracker for BitTorrent generation
        and configures the necessary settings for the tracker server.
        """
        # Install OpenTracker (i2p version)
        self.install_debs(-75, "i2p-opentracker-trusty-server.tgz")

        # Create the OpenTracker tunnel
        json_config = json.dumps(
            {
                "name": "mytrack",
                "website_name": "mytrack.i2p",
                "port": "6969",
                "number_of_tunnels": "5",
            }
        )
        self.add_vm_resource(100, "i2p_create_tunnel.py", json_config)
        self.run_executable(1, "i2p-gen-opentracker-setup.sh", None, True)
