# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Inspired in original code by IBM Corp and Red Hat Inc.
#
# Copyright (C) 2012 IBM Corp.
# Copyright (C) 2014 Red Hat Inc
#
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>
# Author: Stefan Hajnoczi <stefanha@redhat.com>

from avocado.utils import network
from avocado.virt import defaults
from avocado.virt.qemu import path


class QemuDevices(object):

    def __init__(self, params=None):
        self.params = params
        self.qemu_bin = path.get_qemu_binary(params)
        self.redir_port = None
        self._args = [self.qemu_bin]
        self._op_record = []
        self._allocated_ports = []

    def find_free_port(self, start_port, address="localhost"):
        port = start_port
        while ((port in self._allocated_ports) or
               (not network.is_port_free(port, address))):
            port += 1
        self._allocated_ports.append(port)
        return port

    def add_args(self, *args):
        self._args.extend(args)

    def get_cmdline(self):
        return ' '.join(self._args)

    def clone(self, params=None):
        new_devices = QemuDevices(params)
        new_devices._allocated_ports = self._allocated_ports
        for op, args in self._op_record:
            method = getattr(new_devices, op)
            method(**args)
        return new_devices

    def add_fd(self, fd, fdset, opaque, opts=''):
        options = ['fd=%d' % fd,
                   'set=%d' % fdset,
                   'opaque=%s' % opaque]
        if opts:
            options.append(opts)

        self.add_args('-add-fd', ','.join(options))

    def add_qmp_monitor(self, monitor_socket):
        self.add_args('-chardev',
                      'socket,id=mon,path=%s' % monitor_socket,
                      '-mon', 'chardev=mon,mode=control')

    def add_display(self, value='none'):
        self._op_record.append(['add_display', {'value': value}])
        self.add_args('-display', value)

    def add_vga(self, value='none'):
        self._op_record.append(['add_vga', {'value': value}])
        self.add_args('-vga', value)

    def add_nodefaults(self, value='none'):
        self._op_record.append(['add_nodefaults', {}])
        self.add_args('-nodefaults')

    def add_vnc(self, port=None):
        if port is None:
            self.vnc_port = self.find_free_port(5900)
        else:
            self.vnc_port = port
        self._op_record.append(['add_vnc', {'port': port}])
        self.add_args('-vnc', ":%s" % self.vnc_port)

    def add_drive(self, drive_file=None, device_type='virtio-blk-pci',
                  device_id='avocado_image', drive_id='device_avocado_image'):
        """
        Add a drive device to the VM.

        If drive_file is not specified, get the correct path from params.

        :param drive_file: Drive file path (a valid QEMU image file path).
        :param device_type: Type of the drive path added (ide, virtio, scsi).
        :param device_id: String identifying the newly added device.
        :param drive_id: String identifying the newly added drive.
        """
        if drive_file is None:
            drive_file = self.params.get('avocado.args.run.guest_image_path',
                                         defaults.guest_image_path)

        self._op_record.append(['add_drive', {'drive_file': drive_file,
                                              'device_type': device_type,
                                              'device_id': device_id,
                                              'drive_id': drive_id}])
        self.add_args('-drive',
                      'id=%s,if=none,file=%s' %
                      (drive_id, drive_file),
                      '-device %s,id=%s,drive=%s' %
                      (device_type, device_id, drive_id))

    def add_net(self, netdev_type='user', device_type='virtio-net-pci',
                device_id='avocado_nic', nic_id='device_avocado_nic'):
        self._op_record.append(['add_net', {'netdev_type': netdev_type,
                                            'device_type': device_type,
                                            'device_id': device_id,
                                            'nic_id': nic_id}])
        self.redir_port = self.find_free_port(5000)
        self.add_args('-device %s,id=%s,netdev=%s' %
                      (device_type, device_id, nic_id),
                      '-netdev %s,id=%s,hostfwd=tcp::%s-:22' %
                      (netdev_type, nic_id, self.redir_port))

    def add_serial(self, serial_socket, device_id='avocado_serial'):
        self.add_args('-chardev socket,id=%s,path=%s,server,nowait' % (device_id, serial_socket))
        self.add_args('-device isa-serial,chardev=%s' % (device_id))
