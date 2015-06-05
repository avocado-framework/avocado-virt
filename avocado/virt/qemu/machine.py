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
# Copyright (C) 2012 IBM Corp.
# Copyright (C) 2014 Red Hat Inc


import os
import socket
import string
import logging
import tempfile
import uuid as uuid_lib
import threading
import copy

from avocado.core import exceptions
from avocado import aexpect
from avocado.utils import genio
from avocado.utils import process
from avocado.utils import remote
from avocado.utils import wait
from avocado.utils import path as utils_path

from avocado.virt.qemu import monitor
from avocado.virt.qemu import devices
from avocado.virt.qemu import path
from avocado.virt.utils import image
try:
    from avocado.virt.utils import video
    VIDEO_ENCODING_SUPPORT = True
except ImportError:
    VIDEO_ENCODING_SUPPORT = False

log = logging.getLogger("avocado.test")


class VM(object):

    """
    Represents a QEMU Virtual Machine
    """

    def __init__(self, uuid=None, params=None, logdir=None):
        self._popen = None
        self.pid = None
        if params is None:
            params = {}
        self.params = params
        self.devices = devices.QemuDevices(params)
        self.logged = False
        self.remote = None
        if uuid is not None:
            self.uuid = uuid
        else:
            self.uuid = uuid_lib.uuid4()
        self.short_id = str(self.uuid)[:8]
        self.logdir = logdir
        self.screendump_dir = None
        self._screendump_thread_enable = False
        self._screendump_terminate = None
        self._screendump_thread = None
        self._video_enable = False

    def __str__(self):
        if self.pid is None:
            return 'QEMU VM (%s)' % self.short_id
        else:
            return 'QEMU VM (%s PID: %s)' % (self.short_id, self.pid)

    def log(self, msg):
        log.info('%s %s' % (self, msg))

    def _template_build_tags(self):
        only_devices = ' '.join([str(x) for x in self.devices.devices[1:]])
        tags = {'avocado_defaults': self.devices,
                'avocado_devices': only_devices}
        for dev in self.devices.devices:
            tags['avocado_%s' % dev.name] = dev
        return tags

    def _template_apply(self, template, tags):
        cmdline = None
        clean = False
        while not clean:
            try:
                cmdline = template.format(**tags)
            except KeyError, e:
                tag = e.args[0]
                self.log("On qemu template: undefined tag '%s' (ignoring)" % tag)
                template = template.replace('{%s}' % tag, '')
            else:
                clean = True
        return cmdline

    def is_on(self):
        return self._popen is not None

    def power_on(self):
        assert not self.is_on()

        self.monitor_socket = tempfile.mktemp()
        self.devices.add_qmp_monitor(self.monitor_socket)
        self._qmp = monitor.QEMUMonitorProtocol(self.monitor_socket,
                                                server=True)
        self.serial_socket = tempfile.mktemp()
        self.devices.add_serial(self.serial_socket)

        tmpl = self.params.get('contents', '/plugins/virt/qemu/template/*')

        if tmpl is None:
            cmdline = self.devices.get_cmdline()
        else:
            tags = self._template_build_tags()
            cmdline = self._template_apply(tmpl, tags)

        try:
            self._popen = process.SubProcess(cmd=cmdline)
            self.pid = self._popen.start()
            self._qmp.accept()
            self.serial_console = aexpect.ShellSession(
                "nc -U %s" % self.serial_socket,
                auto_close=False,
                output_func=genio.log_line,
                output_params=("serial-console-%s.log" % self.short_id,),
                prompt=self.params.get("shell_prompt", default="[\#\$]"))
            self._screendump_thread_start()
        finally:
            os.remove(self.monitor_socket)

    def power_off(self, migrate=False):
        if self._popen is not None:
            self._screendump_thread_terminate(migrate=migrate)
            self._qmp.cmd('quit')
            self._popen.wait()
            if migrate:
                self.log('Shut down (migration src)')
            else:
                self.log('Shut down')
            self._popen = None
            self.pid = None
            self.serial_console.close()
            os.remove(self.serial_socket)

    def __enter__(self):
        self.power_on()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.power_off()
        return False

    def qmp(self, cmd, verbose=True, **args):
        qmp_args = dict()
        for k in args.keys():
            qmp_args[k.translate(string.maketrans('_', '-'))] = args[k]

        if verbose:
            self.log("-> QMP %s %s" % (cmd, qmp_args))
        retval = self._qmp.cmd(cmd, args=qmp_args)
        if verbose:
            self.log("<- QMP %s" % retval)
        return retval

    def get_qmp_event(self, wait=False):
        return self._qmp.pull_event(wait=wait)

    def get_qmp_events(self, wait=False):
        events = self._qmp.get_events(wait=wait)
        self._qmp.clear_events()
        return events

    def hmp_qemu_io(self, drive, cmd):
        return self.qmp('human-monitor-command',
                        command_line='qemu-io %s "%s"' % (drive, cmd))

    def pause_drive(self, drive, event=None):
        if event is None:
            self.pause_drive(drive, "read_aio")
            self.pause_drive(drive, "write_aio")
            return
        self.hmp_qemu_io(drive, 'break %s bp_%s' % (event, drive))

    def resume_drive(self, drive):
        self.hmp_qemu_io(drive, 'remove_break bp_%s' % drive)

    def login_remote(self, hostname=None, username=None, password=None,
                     port=None, timeout=360):
        if not self.logged:
            if hostname is None:
                hostname = socket.gethostbyname(socket.gethostname())
            if username is None:
                username = self.params.get('user', '/plugins/virt/guest/*')
            if password is None:
                password = self.params.get('password', '/plugins/virt/guest/*')
            if port is None:
                port = self.devices.ports.redir_port
            self.log('Login (Remote) -> '
                     '(hostname=%s, username=%s, password=%s, port=%s)'
                     % (hostname, username, password, port))
            self.remote = remote.Remote(hostname, username, password, port,
                                        timeout=timeout)
            res = self.remote.uptime()
            if res.succeeded:
                self.logged = True

    def clone(self, params=None, preserve_uuid=False):
        """
        Return another VM instance, with the same parameters as current VM.

        This method is mostly used for migrations, although it could be useful
        for other purposes, such a booting a VM that is very similar, with only
        some changed attributes.

        :param params: Dictionary with VM parameters.
        :param preserve_uuid: Whether the clone should preserve its UUID.
        """
        new_vm = VM(uuid=self.uuid, params=self.params, logdir=self.logdir)
        new_vm.devices = self.devices.clone(params)
        return new_vm

    def migrate(self, protocol='tcp'):
        def migrate_complete():
            mig_info = self.qmp("query-migrate")
            mig_status = mig_info['return']['status']
            if mig_status == 'completed':
                self.log("Migration successful")
                return True
            elif mig_status == 'failed':
                raise exceptions.TestFail("Migration of %s failed" % self)
            return False

        clone_params = copy.copy(self.params)
        clone = self.clone(params=clone_params, preserve_uuid=True)
        migration_port = clone.devices.add_incoming(protocol)
        self._screendump_thread_terminate(migrate=True)
        clone.power_on()
        uri = "%s:localhost:%d" % (protocol, migration_port)
        self.qmp("migrate", uri=uri)
        migrate_timeout = self.params.get('timeout',
                                          '/plugins/virt/qemu/migrate/*')
        migrate_result = wait.wait_for(migrate_complete, timeout=float(migrate_timeout),
                                       text='Waiting for migration to complete')
        if migrate_result is None:
            raise exceptions.TestFail("Migration of %s did not complete after %s s" %
                                      (self, migrate_timeout))

        old_vm = VM()
        old_vm.__dict__ = self.__dict__
        self.__dict__ = clone.__dict__
        old_vm.power_off(migrate=True)

    def screendump(self, filename, verbose=True):
        """
        Save a screendump on a given destination.

        It is important to note that QEMU saves screendumps using the PPM
        format.

        :see: http://en.wikipedia.org/wiki/Netpbm_format

        :param filename: Path with the screendump destination.
        :param verbose: Whether to register screendump call into test log
                        (on by default, but has to be turned off in things
                        such as the screendump thread).
        """
        self.qmp(cmd='screendump', verbose=verbose, filename=filename)

    def _screendump_thread_start(self):
        self._screendump_thread_enable = self.params.get('enable',
                                                         '/plugins/virt/screendumps/*')
        video_enable = 'virt.videos.enable'
        self._video_enable = self.params.get('enable',
                                             '/plugins/virt/videos/*')
        if self._screendump_thread_enable:
            self.screendump_dir = utils_path.init_dir(
                os.path.join(self.logdir, 'screendumps', self.short_id))
            self._screendump_terminate = threading.Event()
            self._screendump_thread = threading.Thread(target=self._take_screendumps,
                                                       name='VmScreendumps')
            self._screendump_thread.start()

    def _take_screendumps(self):
        """
        Take screendumps on regular intervals.
        """
        timeout = self.params.get('interval', '/plugins/virt/screendumps/*')
        dump_list = sorted(os.listdir(self.screendump_dir))
        if dump_list:
            last_dump = dump_list[-1].split('.')[0]
            s_index = int(last_dump.split('-')[-1]) + 1
        else:
            s_index = 1

        while True:
            s_ppm_basename = '%04d.ppm' % s_index
            ppm_filename = os.path.join(self.screendump_dir, s_ppm_basename)

            try:
                self.screendump(filename=ppm_filename, verbose=False)
            except socket.error, details:
                self.log("Screendump thread terminated: %s" % details)
                break

            if os.path.isfile(ppm_filename):
                if image.is_ppm(ppm_filename):
                    s_index += 1
                else:
                    self.log("Produced screendump %s is invalid" % ppm_filename)

            if self._screendump_terminate.isSet():
                self._screendump_terminate.clear()
                break
            else:
                self._screendump_terminate.wait(timeout=timeout)

    def _encode_video(self):
        if VIDEO_ENCODING_SUPPORT:
            encoder = video.Encoder(params=self.params, verbose=True)
            video_file = os.path.join(self.logdir, '%s.webm' % self.short_id)
            try:
                encoder.encode(self.screendump_dir, video_file)
            except video.EncodingError, details:
                log.debug(details)

    def _screendump_thread_terminate(self, migrate=False):
        if self._screendump_thread_enable:
            self._screendump_terminate.set()
            if self._video_enable and not migrate:
                self._encode_video()
