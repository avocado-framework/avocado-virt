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
# Copyright: Red Hat Inc. 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

import os
import urllib2

from avocado.plugins import plugin
from avocado.core import output
from avocado.core import data_dir
from avocado.utils import download
from avocado.utils import path
from avocado.utils import crypto
from avocado.utils import process
from avocado.utils import path as utils_path


class VirtBootstrap(plugin.Plugin):

    """
    Implements the avocado 'virt-bootstrap' subcommand
    """

    name = 'virt_bootstrap'
    enabled = True

    def configure(self, parser):
        self.parser = parser.subcommands.add_parser(
            'virt-bootstrap',
            help='Download image files important to avocado virt tests')
        super(VirtBootstrap, self).configure(self.parser)

    def run(self, args):
        fail = False
        view = output.View(app_args=args)
        view.notify(event='message', msg='Probing your system for test requirements')
        try:
            utils_path.find_command('7za')
            view.notify(event='minor', msg='7zip present')
        except utils_path.CmdNotFoundError:
            view.notify(event='warning',
                        msg=("7za not installed. You may "
                             "install 'p7zip' (or the "
                             "equivalent on your distro) to "
                             "fix the problem"))
            fail = True

        jeos_sha1_url = 'https://lmr.fedorapeople.org/jeos/SHA1SUM_JEOS20'
        try:
            view.notify(event='minor',
                        msg=('Verifying expected SHA1 '
                             'sum from %s' % jeos_sha1_url))
            sha1_file = urllib2.urlopen(jeos_sha1_url)
            sha1_contents = sha1_file.read()
            sha1 = sha1_contents.split(" ")[0]
            view.notify(event='minor', msg='Expected SHA1 sum: %s' % sha1)
        except Exception, e:
            view.notify(event='error', msg='Failed to get SHA1 from file: %s' % e)
            fail = True

        jeos_dst_dir = path.init_dir(os.path.join(data_dir.get_data_dir(),
                                                  'images'))
        jeos_dst_path = os.path.join(jeos_dst_dir, 'jeos-20-64.qcow2.7z')

        if os.path.isfile(jeos_dst_path):
            actual_sha1 = crypto.hash_file(filename=jeos_dst_path,
                                           algorithm="sha1")
        else:
            actual_sha1 = '0'

        if actual_sha1 != sha1:
            if actual_sha1 == '0':
                view.notify(event='minor',
                            msg=('JeOS could not be found at %s. Downloading '
                                 'it (173 MB). Please wait...' % jeos_dst_path))
            else:
                view.notify(event='minor',
                            msg=('JeOS at %s is either corrupted or outdated. '
                                 'Downloading a new copy (173 MB). '
                                 'Please wait...' % jeos_dst_path))
            jeos_url = 'https://lmr.fedorapeople.org/jeos/jeos-20-64.qcow2.7z'
            try:
                download.url_download(jeos_url, jeos_dst_path)
            except:
                view.notify(event='warning',
                            msg=('Exiting upon user request (Download '
                                 'not finished)'))
        else:
            view.notify(event='minor',
                        msg=('Compressed JeOS image found '
                             'in %s, with proper SHA1' % jeos_dst_path))

        view.notify(event='minor',
                    msg=('Uncompressing the JeOS image to restore pristine '
                         'state. Please wait...'))
        os.chdir(os.path.dirname(jeos_dst_path))
        result = process.run('7za -y e %s' % os.path.basename(jeos_dst_path),
                             ignore_status=True)
        if result.exit_status != 0:
            view.notify(event='error',
                        msg=('Error uncompressing the image '
                             '(see details below):\n%s' % result))
            fail = True
        else:
            view.notify(event='minor', msg='Successfully uncompressed the image')

        if fail:
            view.notify(event='warning',
                        msg=('Problems found probing this system for tests '
                             'requirements. Please check the error messages '
                             'and fix the problems found'))
        else:
            view.notify(event='message',
                        msg=('Your system appears to be all '
                             'set to execute tests'))
