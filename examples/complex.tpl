/usr/bin/qemu-kvm
-smp 2,sockets=2,cores=2,threads=2
-m 1024
-cpu SandyBridge
-spice port=5900,addr=127.0.0.1,disable-ticketing,seamless-migration=on
-device qxl-vga,id=video0
{avocado_qmp}
{avocado_drive}
{avocado_network}
{avocado_serial}
