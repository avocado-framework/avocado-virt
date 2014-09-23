.. _writing-tests:

==========================
Writing Avocado Virt Tests
==========================

Basic example: Boot test
========================

Avocado virt tests are similar to non-virt ones, they only differ on that
they use some specialized libraries, that let you use special virt features.

Here's an example of a basic virt testing, a test that starts QEMU with a
guest image, then it'll try to establish an ssh connection to this guest::

    from avocado.virt import test


    class boot(test.VirtTest):

        def action(self):
            self.vm.power_on()
            self.vm.login_remote()

        def cleanup(self):
            self.vm.remote.run('shutdown -h now')
            self.vm.power_off()

The base class for the test is ``avocado.virt.test.VirtTest`` instead of the
base ``avocado.test``. The reason for this is that the ``VirtTest`` class can
make the params from the test runner available for tests, and provide other
convenience methods for your tests.

If you chose to not override or extend the default virt test ``setup()`` method,
you'll have at your disposal a basic vm object in ``self.vm``. The VM is not
started (powered on) yet, and you need to start it yourself. Calling
``self.vm.power_on`` starts the QEMU process, then from that point forwards
we are just waiting for the VM to be active. The proof that the VM started and
the guest OS is healthy is that we can establish a remote session (SSH on linux
guests) to it, by using the ``login_remote`` method. That method is going to wait
for a default 60 seconds until the SSH connection is established, and fail in
case the connection can't be established.

If we have an SSH connection, all is good, the test passed, and we're going to
clean things up as a good practice. The ``cleanup`` method is going to run a
``shutdown`` command in the remote connection, and then we proceed to shutting
down the VM (end the QEMU process), through the ``power_off`` method.

If that goes fine as well, the test passed and everybody is happy. We ended
our test with PASS. If any of the operations described above FAIL, avocado is
going to proceed accordingly and FAIL the test.


Basic example: Migrate test
===========================

Now, what if I want to migrate the state of a QEMU VM to another QEMU process
on that very same machine? Here's what a live migration test looks like::

    from avocado.virt import test


    class migration(test.VirtTest):

        def action(self):
            self.vm.power_on()
            migration_mode = self.params.get('migration_mode', 'tcp')
            for _ in xrange(self.params.get('migration_iterations', 4)):
                self.vm.migrate(migration_mode)
                self.vm.login_remote()

        def cleanup(self):
            self.vm.remote.run('shutdown -h now')
            self.vm.power_off()


Fortunately, most of the migration logic is wrapped up
in the method ``vm.migrate``. Here we modeled things after the concept of live
migration, so you have a single vm object, that when migrated keeps working just
as it did work before, with no service interruption (it doesn't care that the
VM state was passed on to another QEMU process). The method will clone the
command line of the current VM, add the appropriate snippets for incoming
migration, start the new process, and call the appropriate ``migrate`` command in
the QMP monitor of the source VM. After it detects the migration is over, we
might repeat the process again ``migration_iteration`` times (here it has the
default value of 4).


More to come
============

This is a basic guide, as the plugin is in heavy developmemt. Soon we'll
have more APIs and cover more cases.
