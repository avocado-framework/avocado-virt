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
from avocado import test
from avocado.utils import process
from avocado.virt import defaults
from avocado.virt.qemu import machine


class VirtTest(test.Test):

    def __init__(self, methodName='runTest', name=None, params=None,
                 base_logdir=None, tag=None, job=None, runner_queue=None):

        if job.args.qemu_bin:
            params['avocado.args.run.qemu_bin'] = job.args.qemu_bin
        if job.args.qemu_dst_bin:
            params['avocado.args.run.qemu_dst_bin'] = job.args.qemu_dst_bin
        if job.args.qemu_img_bin:
            params['avocado.args.run.qemu_img_bin'] = job.args.qemu_img_bin
        if job.args.qemu_io_bin:
            params['avocado.args.run.qemu_io_bin'] = job.args.qemu_io_bin
        if job.args.guest_image_path:
            params['avocado.args.run.guest_image_path'] = job.args.guest_image_path
        if job.args.guest_user:
            params['avocado.args.run.guest_user'] = job.args.guest_user
        if job.args.guest_password:
            params['avocado.args.run.guest_password'] = job.args.guest_password

        params['avocado.args.run.guest_image_restore_test'] = not job.args.disable_restore_image_test

        super(VirtTest, self).__init__(methodName=methodName, name=name,
                                       params=params, base_logdir=base_logdir,
                                       tag=tag, job=job,
                                       runner_queue=runner_queue)

    def restore_guest_images(self):
        """
        Restore any guest images defined in the command line.
        """
        if self.params.get('avocado.args.run.guest_image_path') is None:
            drive_file = defaults.guest_image_path
        else:
            drive_file = self.params.get('avocado.args.run.guest_image_path')
        # Check if there's a compressed drive file
        compressed_drive_file = drive_file + '.7z'
        if os.path.isfile(compressed_drive_file):
            self.log.debug('Found compressed image %s and restore guest '
                           'image set. Restoring image...',
                           compressed_drive_file)
            cwd = os.getcwd()
            os.chdir(os.path.dirname(compressed_drive_file))
            process.run('7za -y e %s' %
                        os.path.basename(compressed_drive_file))
            os.chdir(cwd)
        else:
            self.log.debug('Restore guest image set, but could not find '
                           'compressed image %s. Skipping restore...',
                           compressed_drive_file)

    def setup(self):
        """
        Restore guest image, according to params directives.

        By default, always restore.
        If only the test level restore is disabled, execute one restore (job).
        If both are disabled, then never restore.
        """
        if self.params.get('avocado.args.run.guest_image_restore_test'):
            self.restore_guest_images()
        self.vm = machine.VM(params=self.params, logdir=self.logdir)
        self.vm.devices.add_nodefaults()
        self.vm.devices.add_display('none')
        self.vm.devices.add_vga('std')
        self.vm.devices.add_drive()
        self.vm.devices.add_net()
