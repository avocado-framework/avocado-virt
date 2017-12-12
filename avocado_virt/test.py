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
# Copyright (C) 2014 Red Hat Inc
#
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

import os

from avocado import Test
from avocado.utils import process
from .qemu import machine


class VirtTest(Test):

    def __init__(self, methodName='runTest', name=None, params=None,
                 base_logdir=None, job=None, runner_queue=None):
        super(VirtTest, self).__init__(methodName=methodName, name=name,
                                       params=params, base_logdir=base_logdir,
                                       job=job, runner_queue=runner_queue)
        self.vm = None

    def _restore_guest_images(self):
        """
        Restore any guest images defined in the command line.
        """
        drive_file = self.params.get('image_path', '/plugins/virt/guest/*')
        # Check if there's a compressed drive file
        compressed_drive_file = drive_file + '.xz'
        if os.path.isfile(compressed_drive_file):
            self.log.debug('Found compressed image %s and restore guest '
                           'image set. Restoring image...',
                           compressed_drive_file)
            cwd = os.getcwd()
            os.chdir(os.path.dirname(compressed_drive_file))
            process.run('xz --decompress --keep --force %s' %
                        os.path.basename(compressed_drive_file))
            os.chdir(cwd)
        else:
            self.log.debug('Restore guest image set, but could not find '
                           'compressed image %s. Skipping restore...',
                           compressed_drive_file)

    def setUp(self):
        """
        Restore guest image, according to params directives.

        By default, always restore.
        If only the test level restore is disabled, execute one restore (job).
        If both are disabled, then never restore.
        """
        if not self.params.get('disable_restore_image_test',
                               '/plugins/virt/guest/*'):
            self._restore_guest_images()
        self.vm = machine.VM(params=self.params, logdir=self.logdir)
        self.vm.devices.add_nodefaults()
        self.vm.devices.add_vga('std')
        self.vm.devices.add_vnc()
        self.vm.devices.add_drive()
        self.vm.devices.add_net()
