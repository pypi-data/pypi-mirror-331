import os
import pickle

# >import igraph
import logging

from i2p.i2p_objects import I2PRouter

from firewheel.control.experiment_graph import AbstractPlugin

logging.basicConfig()


class ConfigWebservers(AbstractPlugin):
    """This plugin configures the web servers and also adds zone entries
    to DNS servers that will point to this web server.
    Requirements:
    Principal of operation:
    Caveats:
    """

    # def __init__(self, graph):
    # self.log = logging.getLogger('ConfigWebservers')
    #    self.graph = graph

    def run(self, debug=""):
        return
        self.log = logging.getLogger("ConfigWebservers")
        """ Run the plugin in streaming mode """
        self.log.level = logging.WARNING
        if debug.startswith("T") or debug.startswith("t"):
            self.log.level = logging.INFO
        if debug.startswith("D") or debug.startswith("d"):
            self.log.level = logging.DEBUG

        i2p_bootstrap_dir = "/opt/i2p/bootstrap"

        # The addresses in I2P:
        # "https://reseed.i2p-projekt.de/"
        # "https://netdb.rows.io:444/"
        # "https://i2pseed.zarrenspry.info/"
        # "https://i2p.mooo.com/netDb/"
        # "https://netdb.i2p2.no/"
        # "https://us.reseed.i2p2.no:444/"
        # "https://uk.reseed.i2p2.no:444/"
        # "https://reseed.i2p.vzaws.com:8443/"
        # "https://link.mx24.eu/"
        # "https://ieb9oopo.mooo.com/"
        i2p_sites = {
            "reseed.i2p-projekt.de": {"port": 443},
            "netdb.rows.io": {"port": 444},
            "i2pseed.zarrenspry.info": {"port": 443},
            "i2p.mooo.com": {"port": 443},
            "netdb.i2p2.no": {"port": 443},
            "us.reseed.i2p2.no": {"port": 444},
            "uk.reseed.i2p2.no": {"port": 444},
            "reseed.i2p.vzaws.com": {"port": 8443},
            "link.mx24.eu": {"port": 443},
            "ieb9oopo.mooo.com": {"port": 443},
        }

        s = self.g.find_vertex("i2pbootstrap.internet.net")
        dns = self.g.find_vertex("dns.internet.net")

        web_addr = None
        # >        for iface in s['interfaces']:
        for iface in s.interfaces.interfaces:
            # >            if 'switch' in iface:
            # >                sw = self.g.find_vertex(iface['switch'])
            # >                if 'is_control.network' in sw and sw['is_control.network']:
            # >                    continue
            web_addr = iface["address"]
            break

        self._configure_web_server(s, i2p_bootstrap_dir, i2p_sites)
        self._add_dns_records(dns, web_addr, i2p_sites)

    def _configure_web_server(self, s, i2p_bootstrap_dir, sites):
        """
        Configure the given vertex as a web server for bootstrapping I2P.

        Arguments:
        s -- Vertex to configure as a web server.
        i2p_bootstrap_dir -- Directory for bootstrap files to reside in.
        sites -- List of site names that I2P uses to bootstrap.
        """
        # >        if 'schedule' not in s or not s['schedule']:
        # >            s['schedule'] = []
        # Setup the web server: We will use Nginx.
        # 1. Install the package.
        # >        s['schedule'].append(('install_debs.py', -60, None, 'nginx.tgz', True))
        s.install_debs(-60, "nginx-trusty-server.tgz")
        s.run_executable(-59, "/usr/bin/touch", "/tmp/nginx-installed")

        # 2. Set SSL cert locations and setting for dropper
        # >        ssl_cert_path = '/etc/ssl'
        ssl_cert_path = "/etc/ssl/i2p_ssl_certs_and_keys/"
        ssl_key_path = "%s/private" % (ssl_cert_path)
        # >        reseed_dropper = [
        # >            {'binary_path': '/opt/reseed'}
        # >        ]

        # cert_config = {
        #    'sites': []
        # }
        # for site in sites:
        #    cert_config['sites'].append({
        #        'name': site,
        #        'key_file': '%s/%s.key' % (ssl_key_path, site.replace('.', '_')),
        #        'cert_file': '%s/%s.cert' % (ssl_cert_path, site.replace('.', '_'))
        #    })
        # s['schedule'].append(('generate_certs.py', -59, json.dumps(cert_config), None, True))
        # >        s['schedule'].append(('dropper.py', -59, pickle.dumps([{'binary_path': '/etc/ssl'}]), 'i2p_ssl_certs_and_keys.tgz', True))
        s.drop_file(
            -59, "/etc/ssl/i2p_ssl_certs_and_keys.tgz", "i2p_ssl_certs_and_keys.tgz"
        )
        s.run_executable(
            -58, "tar", "-C /etc/ssl -xf /etc/ssl/i2p_ssl_certs_and_keys.tgz"
        )
        s.run_executable(
            -57, "chown", "-R ubuntu:ubuntu /etc/ssl/i2p_ssl_certs_and_keys"
        )
        s.run_executable(-57, "rm", "-f /etc/ssl/i2p_ssl_certs_and_keys.tgz")

        # 3.a. Drop the files we're going to serve.
        # >        s['schedule'].append(('dropper.py', -57, pickle.dumps(reseed_dropper), 'i2p_reseed_keys.tgz', True))
        s.drop_file(-59, "/opt/reseed/i2p_reseed_keys.tgz", "i2p_reseed_keys.tgz")
        s.run_executable(
            -58, "tar", "-C /opt/reseed -xf /opt/reseed/i2p_reseed_keys.tgz"
        )
        s.run_executable(-57, "chown", "-R ubuntu:ubuntu /opt/reseed/i2p_reseed_keys")
        s.run_executable(-57, "rm", "-f /opt/reseed/i2p_reseed_keys.tgz")
        # 3.b. Install needed packages from deb files.
        # >        s['schedule'].append(('install_debs.py', -56, None, 'i2p-trusty-server.tgz', True))
        s.install_debs(-56, "i2p-trusty-server.tgz")
        # >        s['schedule'].append(('install_debs.py', -55, None, 'expect-trusty-server.tgz', True))
        s.install_debs(-55, "expect-trusty-server.tgz")
        # >        s['schedule'].append(('install_debs.py', -54, None, 'zip-trusty-server.tgz', True))
        s.install_debs(-54, "zip-trusty-server.tgz")

        # 4. Configure the web server.
        # We only configure a single site, since we always serve on 80/443.
        # This makes the assumption that the I2P client doesn't actually check
        # anything and we can feed them whatever we want, regardless of who the
        # client thinks we are.
        # Also, Nginx will accept aliases as its server name option: use this
        # whole list for that option.
        sites_conf = {}
        # Basically copy the nginx default site, tweaking a couple parameters.
        for site in sites.keys():
            ssl_cert = os.path.join(ssl_cert_path, "%s.cert" % site.replace(".", "_"))
            ssl_key = os.path.join(ssl_key_path, "%s.key" % site.replace(".", "_"))
            # I2P seems to try SSL first, possible exclusively. Although this is
            # configurable, we go with the default.
            # We listen HTTP, but configure the correct port for SSL.
            sites_conf[site.replace(".", "_")] = """
server {
    listen 80;
    server_name %s;

    root %s;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
        autoindex on;
    }
}

server {
    listen %d;
    server_name %s;

    root %s;
    index index.html index.htm;

    ssl on;
    ssl_certificate %s;
    ssl_certificate_key %s;

    ssl_session_timeout 5m;

    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers "HIGH:!aNULL:!MD5 or HIGH:!aNULL:!MD5:!3DES";
    ssl_prefer_server_ciphers on;

    location / {
        try_files $uri $uri/ =404;
        autoindex on;
    }
}
    """ % (
                site,
                i2p_bootstrap_dir,
                sites[site]["port"],
                site,
                i2p_bootstrap_dir,
                ssl_cert,
                ssl_key,
            )
            nginx_conf = {
                "sites": sites_conf,
                "conf": {"hashbucket.conf": "server_names_hash_bucket_size 64;"},
            }

        # >        s['schedule'].append(('configure_nginx.py', -50,
        # >            pickle.dumps(nginx_conf), None, True))
        pickled_config = pickle.dumps(nginx_conf, protocol=0).decode()
        s.add_vm_resource(-50, "configure_nginx.py", pickled_config)

        # This agent will wait for 60 I2P RouterInfos.
        # We need to make sure that this will happen.
        self._verify_i2prouter_count()
        # >        s['schedule'].append(('build_reseed_su3.sh', -40,
        # >            None, None, True))
        s.run_executable(-40, "build_reseed_su3.sh", None, True)

    def _verify_i2prouter_count(self):
        i2prouter_count = 0
        for v in self.g.get_vertices():
            # >            if 'is_i2p' in v and v['is_i2p']:
            # >                if v['is_i2p'] == True:
            # >                    i2prouter_count += 1
            if v.is_decorated_by(I2PRouter):
                i2prouter_count += 1

        # We observed 60 RouterInfos when we downloaded a reseed SU3 file
        # on the Internet, so we build ours with 60.
        # assert(i2prouter_count >= 60)
        assert i2prouter_count >= 5

    def _add_dns_records(self, dns, webserver_addr, sites):
        """
        Add A records for the given sites as extra records on the given DNS
        server.

        Arguments:
        dns -- Vertex for the DNS server to work with.
        webserver_addr -- IP address of the web server.
        sites -- List of site names to add records for.
        """
        # Add the various site entries to the DNS server.
        app_data = self._application_data_key(dns, "dns")
        if not app_data:
            app_data = {}
        # Build the addon_records for the web server.
        if "addon_records" in app_data:
            addon_records = app_data["addon_records"]
        else:
            addon_records = {}

        for site in sites:
            tree = site.split(".")
            tree.reverse()

            cur_dict = addon_records
            for t in tree[:-1]:
                if t not in cur_dict:
                    cur_dict[t] = {}
                cur_dict = cur_dict[t]
            cur_dict[tree[-1]] = [("A", webserver_addr)]

        # Get the in-experiment address for the DNS server
        dns_addr = "10.1.1.1"  # Default to what the topology is using.
        # Take the first non-control.address we find.
        # >        for iface in dns['interfaces']:
        for iface in dns.interfaces.interfaces:
            # >            if 'switch' in iface:
            # >                sw = self.g.find_vertex(iface['switch'])
            # >                if 'is_control.network' in sw and sw['is_control.network'] == True:
            # >                    continue
            dns_addr = iface["address"]
            break

        # Add the DNS structure to application data.
        if "domains" in app_data:
            if ".net" not in app_data["domains"]:
                app_data["domains"].append(".net")
        else:
            app_data["domains"] = [".net"]

        if "dns_address" not in app_data:
            app_data["dns_address"] = dns_addr

        # addon_records already merged the existing records. Update it.
        app_data["addon_records"] = addon_records

        # Update the vertex.
        self._add_application_data(dns, {"dns": app_data})

    # --------------------------- Utilities -------------------------------

    def _add_application_data(self, node, dictionary):
        """Adds or updates the dictionary to the node's application_data slot
        Note: This gives each node in the graph a key called
              'application_data' which is a dictionary (key/value)
              Each application then can create a key entry that
              will typically be another dictionary.
        Note: If a key value in the dictionary is already used, this
            will override it.
        """
        if "application_data" in node and type(node["application_data"]) == dict:
            node["application_data"].update(dictionary)
        else:
            node["application_data"] = dictionary

    def _application_data(self, node):
        """Gets the dictionary to the node's application_data slot"""
        if "application_data" in node and type(node["application_data"]) == dict:
            return node["application_data"]
        else:
            return {}

    def _application_data_key(self, node, key):
        """Returns the given key from the node labeled application_data
        This assumes that 'application_data' is a dictionary
        with keys provided by the application. Calling it gives
        the value behind the key you are looking for.
        """
        d = self._application_data(node)
        return d.get(key)
