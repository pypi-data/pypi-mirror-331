.. _i2p_mc_repo:

******************
firewheel_repo_i2p
******************

.. warning::

    This repository was last updated in 2021 and is considered research-quality code.
    This is provided to the open source community as an example of how Emuytics experiments facilitate the exploration of large distributed systems.

This repository was used as the model behind:

Stickland, Michael, Li, Justin D., Swiler, Laura Painton, & Tarman, Thomas (2021). Foundations of Rigorous Cyber Experimentation. https://doi.org/10.2172/1854751

The ``firewheel_repo_i2p`` repo contains a FIREWHEEL model that you can use to define and execute experiments using the Invisible Internet Project (i2p) software, a large scale, distributed, anonymization network that rides on top of the internet.
i2p is attributed as being an enabling technology for what's commonly known as the Dark Web.

Due to licensing limitations, we are unable to provide the expected binary files (VM Resources nor Images) that are used within these model components.
Please contact us if there are issues replicating the creation of the VM Resources.

Included Model Components
=========================

There are several model components (MCs) in the i2p Firewheel model:

*  ``i2p.topology`` - Defines/creates the overall network topology, consisting of  L1 and L2 BGP routers, L3 sub-nets containing 1 or more i2p routers, as well as a data center with NTP, DNS, and other services used by the i2p network. Requires a network size parameter to be specified, ``i2p.topology:<size>``, an integer indicating the approximate number of i2p routers to be in the network. There are always 31 L1 BGP routers, and the number of L2 BGP routers and L3 sub-nets will be determined based on the requested network size.

*  ``i2p.objects`` - Contains definitions for i2p routers, including some specialty servers located in the data center, and the VM resources used for provisioning them during startup.

*  ``i2p.config_floodfills`` - Configures 6% of i2p routers in a topology to be Floodfill DHT (distributed hash table) servers. Also configures each i2p router to have a startup bandwidth rate, and then a default rate for use after startup (the rates are currently hard coded). Contains related VM resources.

*  ``i2p.config_snark`` - Configures groups of non-floodfill i2p routers to utilize the Snark torrenting capability within i2p to generate background traffic within the i2p network. Some will be configured as Generators (eepsites), some as Seeders, and others as Leechers depending on the chosen (hard coded) ratio settings. Contains related VM resources.

*  ``i2p.config_bandwidth`` - Configures i2p router software with each router's advertised bandwidth and bandwidth share percent settings, which are used by the i2p software during execution. Contains related VM resources.

*  ``i2p.config_webservers`` - *[deprecated]* Configures some i2p routers to be webserver-based eepsites, which are accessed by other i2p nodes to generate background i2p network traffic. Contains related vm resources. This has been replaced in the current model by the use of Snark.

*  ``i2p.config_victims`` - Configures groups of 1 or more i2p routers, all with the same settings as specified in the *i2p_config_victims/victim_group_configs.json* file. Victim properties that can be specified are Snark/torrenting role (Seeder, Leecher, or None), machine Bandwidth (KB/s) and number of CPU Cores, and the i2p Shared Bandwidth Percentage (0 - 100). The number of i2p routers per victim (i.e. sample) group, and the number of duplicate sets of victim groups (both currently hard coded) may be specified to meet specific experimental needs.

*  ``i2p.setup`` - This is simply a command line shortcut, which ensures that all i2p MCs that other MCs depend on, but which are not listed explicitly on the command line, will be executed as needed.

*  ``i2p.multiple_clients`` - Research code that allows multiple instances of i2p routers to be installed concurrently on a single machine. Contact us for information and updates related to this MC. This has not been tested with the rest of these i2p MCs.

Running i2p experiments
=======================

The i2p main branch contains code that, when last tested, is compatible with 
FIREWHEEL version 2.5 and later.

To launch an i2p experiment you must include the ``i2p.topology:<size>`` and the ``i2p.setup`` MCs on the command line, in that order, along with the appropriate launch MC, (e.g., ``firewheel experiment i2p.topology:1000 i2p.setup minimega.launch``)

Any additional MCs required to run an i2p experiment are included add attribute dependencies in the ``i2p_setup/MANIFEST`` file, and are not required on the command line.
Also, since the order of execution of these MCs that an experiment depends on is very important, it's best not to list manually on the command line unless you know exactly what you're doing.

If you don't want to configure victim groups, simply comment out the "i2p_victims" attribute dependency in the ``i2p_setup/MANIFEST`` file.
Otherwise, groups of i2p routers will be configured as described above.


Using different versions of I2P software
========================================

In the ``i2p_objects/vm_resources`` folder there are two different versions of the
i2p software referenced:

* i2p-0.9.45-trusty-desktop.tgz - I2P Version 0.9.45
* i2p_0.9.47x-2~xenial+1_debs.tgz - I2P Version 0.9.47

The 0.9.45 version works on Ubuntu 14.04 (Trusty) Desktop operating system while the 0.9.47 is designed for Ubuntu 16.04 (Xenial).The packages should include the i2p router software and any additional software packages required by i2p.

However, just remember, *there are no guarantees or warrantees associated with this software*, and *not all the MCs have NOT been tested with the 0.9.45 version of the i2p software*!
