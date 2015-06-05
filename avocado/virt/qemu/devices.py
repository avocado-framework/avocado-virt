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
# Author: Ruda Moura <rmoura@redhat.com>

from avocado.utils import network
from avocado.utils.data_structures import Borg
from avocado.virt import defaults
from avocado.virt.qemu import path


class UnsupportedMigrationProtocol(Exception):
    pass


class UnknownQemuDevice(Exception):
    pass


class PortTracker(Borg):

    """
    Tracks ports used in the host machine.
    """

    def __init__(self):
        Borg.__init__(self)
        self.address = 'localhost'
        self.start_port = 5000
        if not hasattr(self, 'retained_ports'):
            self._reset_retained_ports()

    def __str__(self):
        return 'Ports tracked: %r' % self.retained_ports

    def _reset_retained_ports(self):
        self.retained_ports = []

    def register_port(self, port):
        if ((port not in self.retained_ports) and
                (network.is_port_free(port, self.address))):
            self.retained_ports.append(port)
        else:
            raise ValueError('Port %d in use' % port)
        return port

    def find_free_port(self, start_port=None):
        if start_port is None:
            start_port = self.start_port
        port = start_port
        while ((port in self.retained_ports) or
               (not network.is_port_free(port, self.address))):
            port += 1
        self.retained_ports.append(port)
        return port

    def release_port(self, port):
        if port in self.retained:
            self.retained.remove(port)


class QemuDevice(object):

    """
    Abstract Qemu device.

    Here, 'device' means a part of the QEMU command line.
    Although not all qemu command line parts represent a
    device, most of them do, so arguably one could consider
    this a reasonable abstraction.
    """

    name = 'qemu_device'

    def __init__(self):
        self._args = []
        self.ports = PortTracker()

    def __repr__(self):
        return '%s(name=%r)' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.get_cmdline()

    def get_cmdline(self):
        # pylint: disable=E1124
        return ' '.join(self._args).format(self=self)

    def clone(self):
        return self


class QemuDeviceGeneric(QemuDevice):

    name = 'generic'

    def __init__(self, cmdline):
        QemuDevice.__init__(self)
        self.cmdline = cmdline
        self._args = cmdline.split()


class QemuBinary(QemuDevice):

    """
    The Qemu binary.
    """

    name = 'qemu_binary'

    def __init__(self, path='/bin/qemu-kvm'):
        QemuDevice.__init__(self)
        self.path = path
        self._args = ['{self.path}']


class QemuDeviceNoDefaults(QemuDevice):

    """
    Don't create default devices.
    """

    name = 'nodefaults'

    def __init__(self):
        QemuDevice.__init__(self)
        self._args = ['-nodefaults']


class QemuDeviceDisplay(QemuDevice):

    """
    Display options.
    """

    name = 'display'

    def __init__(self, kind='none'):
        QemuDevice.__init__(self)
        self.kind = kind
        self._args = ['-display {self.kind}']


class QemuDeviceVGA(QemuDevice):

    """
    Video card.
    """

    name = 'vga'

    def __init__(self, video_card='none'):
        QemuDevice.__init__(self)
        self.video_card = video_card
        self._args = ['-vga {self.video_card}']


class QemuDeviceVNC(QemuDevice):

    """
    VNC Server.
    """

    name = 'vnc'

    def __init__(self, port):
        QemuDevice.__init__(self)
        self.port = port
        self._args = ['-vnc :{self.port}']

    def clone(self):
        self.port = self.ports.find_free_port(self.port + 5900) - 5900
        return self


class QemuDeviceQMP(QemuDevice):

    """
    QMP monitor.
    """

    name = 'qmp'

    def __init__(self, socket):
        QemuDevice.__init__(self)
        self.socket = socket
        self._args = ['-chardev socket,id=mon,path={self.socket}',
                      '-mon chardev=mon,mode=control']


class QemuDeviceSerial(QemuDevice):

    """
    Serial port.
    """

    name = 'serial'

    def __init__(self, socket, device_id='avocado_serial'):
        QemuDevice.__init__(self)
        self.socket = socket
        self.device_id = device_id
        self._args = ['-chardev socket,id={self.device_id},path={self.socket},server,nowait',
                      '-device isa-serial,chardev={self.device_id}']


class QemuDeviceFD(QemuDevice):

    """
    Floppy drive.
    """

    name = 'fd'

    def __init__(self, fd, fdset, opaque, opts):
        QemuDevice.__init__(self)
        self.fd = fd
        self.set = fdset
        self.opaque = opaque
        self._args = ['-add-fd fd={self.fd} set={self.set} opaque={self.opaque}']
        if opts:
            self._args.extend(opts)


class QemuDeviceDrive(QemuDevice):

    """
    Disk drive.
    """

    name = 'drive'

    def __init__(self, drive_file, device_type='virtio-blk-pci',
                 device_id='avocado_image', drive_id='device_avocado_image'):
        QemuDevice.__init__(self)
        self.drive_file = drive_file
        self.device_type = device_type
        self.device_id = device_id
        self.drive_id = drive_id
        self._args = ['-drive id={self.drive_id},if=none,file={self.drive_file}',
                      '-device {self.device_type},id={self.device_id},drive={self.drive_id}']


class QemuDeviceNetwork(QemuDevice):

    """
    Network device.
    """

    name = 'network'

    def __init__(self, redir_port,
                 netdev_type='user', device_type='virtio-net-pci',
                 device_id='avocado_nic', nic_id='device_avocado_nic'):
        QemuDevice.__init__(self)
        self.redir_port = redir_port
        self.netdev_type = netdev_type
        self.device_type = device_type
        self.device_id = device_id
        self.nic_id = nic_id
        self._args = ['-device {self.device_type},id={self.device_id},netdev={self.nic_id}',
                      '-netdev {self.netdev_type},id={self.nic_id},hostfwd=tcp::{self.ports.redir_port}-:22']

    def clone(self):
        self.ports.redir_port = self.ports.find_free_port(self.ports.redir_port)
        self.redir_port = self.ports.redir_port
        return self


class QemuDeviceIncoming(QemuDevice):

    """
    Incoming migration.
    """

    name = 'incoming'

    def __init__(self, protocol='tcp', port=5000):
        QemuDevice.__init__(self)
        self.protocol = protocol
        self.port = port
        self._args = ['-incoming {self.protocol}:0:{self.port}']


class QemuDevices(object):

    def __init__(self, params=None):
        self.params = params
        self.qemu_bin = path.get_qemu_binary(params)
        self.devices = [QemuBinary(self.qemu_bin)]
        self.ports = PortTracker()
        self._qemu_device_classes = list(cls for cls in QemuDevice.__subclasses__())

    def __str__(self):
        return self.get_cmdline()

    def add_device(self, name_or_class, **kwargs):
        dev = None
        for cls in self._qemu_device_classes:
            if name_or_class == cls.name or name_or_class == cls:
                dev = cls(**kwargs)
                self.devices.append(dev)
        if dev is None:
            raise UnknownQemuDevice(name_or_class)

    def remove_device(self, name_or_class):
        not_found = True
        for dev in list(self.devices):
            if dev.name == name_or_class or dev.__class__ == name_or_class:
                self.devices.remove(dev)
                not_found = False
                break
        if not_found:
            raise ValueError('%s not in devices' % name_or_class)

    def has_device(self, name_or_class):
        not_found = False
        for dev in self.devices:
            if dev.name == name_or_class or dev.__class__ == name_or_class:
                not_found = True
                break
        return not_found

    def get_cmdline(self):
        devices = [str(dev) for dev in self.devices]
        return ' '.join(devices)

    def clone(self, params=None):
        new_qemu_devices = QemuDevices(params)
        new_qemu_devices.devices = list(self.devices)
        for exclude in ['qmp', 'serial', 'fd', 'incoming']:
            try:
                new_qemu_devices.remove_device(exclude)
            except ValueError:
                pass
        for dev in new_qemu_devices.devices:
            dev.clone()
        return new_qemu_devices

    def add_nodefaults(self):
        self.add_device('nodefaults')

    def add_display(self, kind='none'):
        self.add_device('display', kind=kind)

    def add_vga(self, video_card='none'):
        self.add_device('vga', video_card=video_card)

    def add_vnc(self, port=None):
        if port is None:
            port = self.ports.find_free_port(5900)
        else:
            self._port.register_port(port)
        self.add_device('vnc', port=port - 5900)    # vnc :0 == port 5900

    def add_qmp_monitor(self, monitor_socket):
        self.add_device('qmp', socket=monitor_socket)

    def add_fd(self, fd, fdset, opaque, opts=None):
        self.add_device('fd', fd=fd, fdset=fdset, opaque=opaque, opts=opts)

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
            drive_file = self.params.get('image_path', '/plugins/virt/guest/*')
        self.add_device('drive', drive_file=drive_file, device_type=device_type,
                        device_id=device_id, drive_id=drive_id)

    def add_net(self, netdev_type='user', device_type='virtio-net-pci',
                device_id='avocado_nic', nic_id='device_avocado_nic'):
        self.ports.redir_port = self.ports.find_free_port(5000)
        self.add_device('network', redir_port=self.ports.redir_port,
                        netdev_type=netdev_type, device_type=device_type,
                        device_id=device_id, nic_id=nic_id)

    def add_serial(self, serial_socket, device_id='avocado_serial'):
        self.add_device('serial', socket=serial_socket, device_id=device_id)

    def add_incoming(self, protocol):
        if protocol == 'tcp':
            self.ports.migration_tcp_port = self.ports.find_free_port(5000)
            self.add_device('incoming', protocol=protocol, port=self.ports.migration_tcp_port)
        else:
            msg = 'Migration %s still unsupported' % protocol
            raise UnsupportedMigrationProtocol(msg)
        return self.ports.migration_tcp_port

    def add_cmdline(self, cmdline):
        self.add_device('generic', cmdline=cmdline)
