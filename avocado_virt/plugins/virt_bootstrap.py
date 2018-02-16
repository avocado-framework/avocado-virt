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

import logging
import os
import urllib2

from avocado.core import data_dir
from avocado.utils import download
from avocado.utils import path
from avocado.utils import crypto
from avocado.utils import process
from avocado.utils import path as utils_path

# Avocado's plugin interface module has changed location. Let's keep
# compatibility with old for at, least, a new LTS release
try:
    from avocado.core.plugin_interfaces import CLICmd
except ImportError:
    from avocado.plugins.base import CLICmd


LOG = logging.getLogger("avocado.app")


class VirtBootstrap(CLICmd):

    """
    Implements the avocado 'virt-bootstrap' subcommand
    """

    name = 'virt-bootstrap'
    description = "Avocado-Virt 'virt-bootstrap' subcommand"

    def run(self, args):
        fail = False
        LOG.info('Probing your system for test requirements')
        try:
            utils_path.find_command('xz')
            logging.debug('xz present')
        except utils_path.CmdNotFoundError:
            LOG.warn("xz not installed. You may install xz (or the "
                     "equivalent on your distro) to fix the problem")
            fail = True

        jeos_sha1_url = ("https://avocado-project.org/data/assets/jeos/25/"
                         "SHA1SUM_JEOS25")
        try:
            LOG.debug('Verifying expected SHA1 sum from %s', jeos_sha1_url)
            sha1_file = urllib2.urlopen(jeos_sha1_url)
            sha1_contents = sha1_file.read()
            sha1 = sha1_contents.split(" ")[0]
            LOG.debug('Expected SHA1 sum: %s', sha1)
        except Exception, exc:
            LOG.error('Failed to get SHA1 from file: %s', exc)
            fail = True
            sha1 = "FAILED TO GET DOWNLOADED FROM AVOCADO-PROJECT"

        jeos_dst_dir = path.init_dir(os.path.join(data_dir.get_data_dir(),
                                                  'images'))
        jeos_dst_path = os.path.join(jeos_dst_dir, 'jeos-25-64.qcow2.xz')

        if os.path.isfile(jeos_dst_path):
            actual_sha1 = crypto.hash_file(filename=jeos_dst_path,
                                           algorithm="sha1")
        else:
            actual_sha1 = '0'

        if actual_sha1 != sha1:
            if actual_sha1 == '0':
                LOG.debug('JeOS could not be found at %s. Downloading '
                          'it (205 MB). Please wait...', jeos_dst_path)
            else:
                LOG.debug('JeOS at %s is either corrupted or outdated. '
                          'Downloading a new copy (205 MB). '
                          'Please wait...', jeos_dst_path)
            jeos_url = ("https://avocado-project.org/data/assets/jeos/25/"
                        "jeos-25-64.qcow2.xz")
            try:
                download.url_download(jeos_url, jeos_dst_path)
            except:
                LOG.warn('Exiting upon user request (Download not finished)')
        else:
            LOG.debug('Compressed JeOS image found in %s, with proper SHA1',
                      jeos_dst_path)

        LOG.debug('Uncompressing the JeOS image to restore pristine '
                  'state. Please wait...')
        os.chdir(os.path.dirname(jeos_dst_path))
        cmd = 'xz --keep --force -d %s' % os.path.basename(jeos_dst_path)
        result = process.run(cmd, ignore_status=True)
        if result.exit_status != 0:
            LOG.error('Error uncompressing the image (see details below):\n%s',
                      result)
            fail = True
        else:
            LOG.debug('Successfully uncompressed the image')

        if fail:
            LOG.warn('Problems found probing this system for tests '
                     'requirements. Please check the error messages '
                     'and fix the problems found')
        else:
            LOG.info('Your system appears to be all set to execute tests')
