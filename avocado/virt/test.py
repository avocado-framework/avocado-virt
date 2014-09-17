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

from avocado import test


class VirtTest(test.Test):

    def __init__(self, methodName='runTest', name=None, params=None,
                 base_logdir=None, tag=None, job=None, runner_queue=None):

        if job.args.qemu_bin:
            params['qemu_bin'] = job.args.qemu_bin
        if job.args.qemu_dst_bin:
            params['qemu_dst_bin'] = job.args.qemu_dst_bin
        if job.args.guest_image_path:
            params['guest_image_path'] = job.args.guest_image_path

        super(VirtTest, self).__init__(methodName=methodName, name=name,
                                       params=params, base_logdir=base_logdir,
                                       tag=tag, job=job,
                                       runner_queue=runner_queue)
