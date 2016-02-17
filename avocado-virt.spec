%global modulename avocado
%if ! 0%{?commit:1}
 %define commit bda495c11d68d9d5a4f25d3ffcaa7a880b999bc8
%endif
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Summary: Avocado Virt Plugin
Name: avocado-virt
Version: 0.33.0
Release: 0%{?dist}
License: GPLv2
Group: Development/Tools
URL: http://avocado-framework.readthedocs.org/
Source0: https://github.com/avocado-framework/%{name}/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRequires: python2-devel, python-setuptools
BuildArch: noarch
Requires: python, avocado, aexpect

%description
Avocado Virt is a plugin that allows users to run virtualization related
tests in avocado. Up to this point, QEMU/KVM is the only backend supported.

%prep
%setup -q -n %{name}-%{commit}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root %{buildroot} --skip-build

%files
%defattr(-,root,root,-)
%dir /etc/avocado
%dir /etc/avocado/conf.d
%config(noreplace)/etc/avocado/conf.d/virt.conf
%doc README.rst LICENSE
%exclude %{python_sitelib}/avocado_virt/utils/video.py*
%{python_sitelib}/avocado_virt*

%package video
Summary: Avocado Virt VM Video Support
Requires: avocado-virt, python-pillow, gstreamer1-plugins-good, gobject-introspection

%description video
This Avocado Virt Plugin subpackage allows you to encode videos from vms
during avocado virt tests.

%files video
%{python_sitelib}/avocado_virt/utils/video.py*

%changelog
* Wed Feb 17 2016 Cleber Rosa <cleber@redhat.com> - 0.33.0-0
- New upstream release 0.33.0

* Wed Dec 23 2015 Cleber Rosa <cleber@redhat.com> - 0.31.0-0
- New upstream release 0.31.0

* Thu Nov  5 2015 Cleber Rosa <cleber@redhat.com> - 0.30.0-0
- New upstream release 0.30.0

* Wed Aug 7 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.29.0-1
- New upstream release 0.29.0

* Mon Aug 3 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.27.0-1
- New upstream release 0.27.0

* Tue Jul 6 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.26.0-1
- New upstream release 0.26.0

* Tue Jun 16 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.25.0-1
- New upstream release 0.25.0

* Fri May 22 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.24.0-2
- Fix issue with migration timeout settings

* Mon May 18 2015 Ruda Moura <rmoura@redhat.com> - 0.24.0-1
- New upstream release

* Mon Apr 21 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.23.0-1
- New upstream release

* Mon Oct 13 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.14.0-1
- New upstream release (sync releases with avocado releases)

* Mon Sep 22 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.3-1
- New upstream release

* Wed Sep  3 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.2-1
- New upstream release

* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.1-1
- New upstream release

* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.0-1
- First RPM
