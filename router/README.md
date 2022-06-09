
The routers are VyOS (https://vyos.io/) images running with Qemu in
the GNS3 emulator.

By default, the appliance is configured to run in Qemu with KVM
acceleration and the -cpu flag set to host. GNS3 must be configured to
enable KVM. Check it in Edit > Preferences > QEMU.

Also if GNS3 is running inside a VM, enable nested virtualization in
the VM.

The appliance is also configured to use the "virtio-net-pci" network
adapter type instead of the default "e1000" for better network performance.


The configuration for each router are located in the scripts inside
the `backbone` and `locations` directories. The topology builder
script uses the configuration scripts to automatically configure the
routers in the topology.


Router interfaces after the configuration:

![simplified topology](./router_topology.png)

