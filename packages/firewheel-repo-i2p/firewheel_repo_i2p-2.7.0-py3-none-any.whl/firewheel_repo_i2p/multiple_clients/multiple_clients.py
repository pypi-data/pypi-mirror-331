from i2p.i2p_objects import I2PRouter

from firewheel.control.experiment_graph import AbstractPlugin


class MultipleClients(AbstractPlugin):
    """
    Increases I2P routers with similarly configured multiple clients.
    """

    def run(self, count=4):
        """
        Executes the plugin to install agents for running multiple clients.

        This method installs the necessary packages and executes scripts
        to configure and run the specified number of clients on each I2P router.

        Args:
            count (int, optional): The number of clients to run on each I2P router (default is 4).
        """
        assert count.isnumeric()

        self.count = int(count)

        for v in self.g.get_vertices():
            if v.is_decorated_by(I2PRouter):
                v.install_debs(-33, "ubuntu14043desktop-bridge_utils.tgz")
                v.run_executable(-32, "prep_multiple_clients.sh", None, True)
                v.run_executable(
                    -5, "build_multiple_clients.sh", "%d" % self.count, True
                )
                v.run_executable(60, "run_multiple_clients.sh", "%d" % self.count, True)
