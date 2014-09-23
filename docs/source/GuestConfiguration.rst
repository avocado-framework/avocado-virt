.. _guest-config:

===================
Guest Configuration
===================

By default, avocado-virt uses an x86_64 minimal guest image based on the latest
stable version of Fedora available at a given time. The image file is a
compressed qcow2 image located on my image repository that is downloaded,
should you choose to run the sub command ``virt-bootstrap``.

If you use avocado with default settings, the test runner is going to uncompress
the pristine image of this so-called JeOS before each test. You may provide both
--disable-restore-image-test and --disable-restore-image-job options if you want
to completely skip the backup restore process.

Or, you may opt for using your own guest image in your tests.

==================
Guest Requirements
==================

The JeOS is a fairly small guest, so your guest should be generally fine, as
long as it does have open SSH running on port 22 after boot, for all the
tests that require SSH connections (that is, tests that at some point call the
VM method ``.login_remote()``. That said, it is hard to keep requirements
documented with precision, given that the tests and the plugin are going to
evolve in scope and features. Please feel free to send us patches to this
documentation file to correct any inaccuracies.

====================
Using your own image
====================

You can use your own image by specifying the following options:

* ``--guest-image-path`` - You can provide this option with an arbitrary path
  to a qemu disk image file with your guest. You can use any of the file formats
  specified, such as qcow2, qed or even raw image formats.

* ``--guest-user`` - If your image has a specific user set up previously that
  you want avocado to use when logging into the remote guest, please provide
  this option. Avocado will inform the default values used in the
  ``avocado run --help`` output.

* ``--guest-password`` - If your image has a specific password for the user set
  up previously that you want avocado to use when logging into the remote guest,
  please provide this option. Avocado will inform the default values used in the
  ``avocado run --help`` output. Note that a previous setup of ssh keys on that
  guest can let you ignore that option entirely.

Next, we'll learn how to write a simple test, using the avocado basic APIs.