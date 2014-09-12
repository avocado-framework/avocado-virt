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

    from avocado import job
    from avocado.core import data_dir
    from avocado.virt import test
    from avocado.virt.qemu import machine


    class boot(test.VirtTest):

        def setup(self):
            self.vm = machine.VM(self.params)
            self.vm.devices.add_display('none')
            self.vm.devices.add_vga('none')
            drive_file = data_dir.get_datafile_path('images', 'jeos-20-64.qcow2')
            self.vm.devices.add_drive(drive_file)
            self.vm.devices.add_net()

        def action(self):
            self.vm.launch()
            self.vm.setup_remote_login()

        def cleanup(self):
            self.vm.remote.run('shutdown -h now')
            self.vm.shutdown()


    if __name__ == "__main__":
        job.main()

The base class for the test is `avocado.virt.test.VirtTest` instead of the
base `avocado.test`. The reason for this is that the `VirtTest` class can
make the params from the test runner available for tests, and provide other
convenience methods for your tests.

Then we get to the VM instantiation step: The virt library provides you with
the `avocado.virt.qemu.machine.VM` class, that models a QEMU based VM. This
class has the `devices` attribute, an object that stores the devices present
in that particular virtual machine. In QEMU, devices are represented by
command line options, and the devices attribute stores and translates specified
devices to a command line. In our example, after the VM class is instantiated,
we add `display` and `vga` devices, as well as a `drive` (containing the
JeOS image) and a `net` device was added. This makes up for the setup of our
test.

Then we go to the `action` method. We call `launch`, that starts the QEMU
process, then from that point forwards we are just waiting for the VM to be
active. The proof that the VM started and the guest OS is healthy is that we
can establish a remote session to it, by using the `setup_remote_login` method.
That method is going to wait for a default 60 seconds until the SSH connection
is established.

If we have an SSH connection, all is good, and we're going to clean things up.
The `cleanup` method is going to run a `shutdown` command in the SSH connection,
and then we proceed to shutting down the VM, through the `shutdown` method.

If that goes fine as well, the test passed and everybody is happy. We ended
our test with PASS. If any of the operations described above FAIL, avocado is
going to proceed accordingly and FAIL the test.


Basic example: Migrate test
===========================

Now, what if I want to migrate the state of a QEMU VM to another QEMU process
on that very same machine? Here's what a live migration test looks like::

    from avocado import job
    from avocado.core import data_dir
    from avocado.virt import test
    from avocado.virt.qemu import machine


    class migration(test.VirtTest):

        def setup(self):
            self.vm = machine.VM(self.params)
            self.vm.devices.add_display('none')
            self.vm.devices.add_vga('none')
            drive_file = data_dir.get_datafile_path('images', 'jeos-20-64.qcow2')
            self.vm.devices.add_drive(drive_file)
            self.vm.devices.add_net()
            self.vm.launch()
            self.vm.setup_remote_login()

        def action(self):
            migration_mode = self.params.get('migration_mode', 'tcp')
            for _ in xrange(self.params.get('migration_iterations', 4)):
                self.vm.migrate(migration_mode)
                self.vm.setup_remote_login()

        def cleanup(self):
            self.vm.remote.run('shutdown -h now')
            self.vm.shutdown()


    if __name__ == "__main__":
        job.main()

Here you see the basic same idea as in the `boot` test, except that now we
are only interested in the migration part, so we can move the `setup_remote_login`
to the setup stage. Fortunately, most of the migration logic is wrapped up
in the method `vm.migrate`. It will clone the command line for your current
VM, add the appropriate snippets for incoming migration, start the new process,
and call the appropriate `migrate` command in the QMP monitor of the source
VM. After it detects the migration is over, we might repeat the process
again, for as long as we see fit.


More to come
============

This is a basic guide, as the plugin is in heavy developmemt. Soon we'll
have more APIs and cover more cases.
