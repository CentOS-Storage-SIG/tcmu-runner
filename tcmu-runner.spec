# To disable particular handlers, remove the comment and space
#% global without_glfs -Dwith-glfs=FALSE
%global without_rbd -Dwith-rbd=FALSE

Name:           tcmu-runner
License:        ASL 2.0
Group:          System Environment/Daemons
Summary:        A daemon that supports LIO userspace backends
Version:        1.3.0
%global         candidate    rc4
Release:        %{?candidate:0.}2%{?candidate}%{?dist}
URL:            https://github.com/open-iscsi/tcmu-runner
Source:         %{url}/archive/v%{version}%{?candidate:-%{candidate}}.tar.gz#/%{name}-%{version}%{?candidate:-%{candidate}}.tar.gz
# patch from https://github.com/open-iscsi/tcmu-runner/pull/322
Patch1:         duplicate_struct_iovec.patch
BuildRequires:  cmake glib2-devel libnl3-devel zlib-devel kmod-devel
%if 0%{!?without_glfs:1}
BuildRequires:  glusterfs-api-devel
%endif
%if 0%{!?without_rbd:1}
BuildRequires:  librbd1-devel
%endif
Requires:       targetcli

%description
A daemon that handles the complexity of the LIO kernel target's userspace
passthrough interface (TCMU). It presents a C plugin API for extension modules
that handle SCSI requests in ways not possible or suitable to be handled
by LIO's in-kernel backstores.

%if 0%{!?without_glfs:1}
%package handler-glfs
Summary:        Gluster handler for tcmu-runner
Requires:       %{name} = %{version}-%{release}

%description handler-glfs
A daemon that handles the complexity of the LIO kernel target's userspace
passthrough interface (TCMU). It presents a C plugin API for extension modules
that handle SCSI requests in ways not possible or suitable to be handled
by LIO's in-kernel backstores.

This package contains the Gluster handler.
%endif

%if 0%{!?without_rbd:1}
%package handler-rbd
Summary:        Ceph RBD handler for tcmu-runner
Requires:       %{name} = %{version}-%{release}

%description handler-rbd
A daemon that handles the complexity of the LIO kernel target's userspace
passthrough interface (TCMU). It presents a C plugin API for extension modules
that handle SCSI requests in ways not possible or suitable to be handled
by LIO's in-kernel backstores.

This package contains the Ceph RBD handler.
%endif

%package -n libtcmu
Summary:        A library to ease supporting LIO userspace processing
Group:          System Environment/Libraries
# for upgrades, we're removing libtcmu-devel
Obsoletes:      libtcmu-devel < %{version}-%{release}

%description -n libtcmu
libtcmu provides a library for processing SCSI commands exposed by the
LIO kernel target's TCM-User backend.

%package -n libtcmu-devel
Summary:        Development headers for libtcmu
Group:          System Environment/Libraries
Requires:       %{name} = %{version}-%{release}

%description -n libtcmu-devel
Development header(s) for developing against libtcmu.

%prep
%setup -q -n %{name}-%{version}%{?candidate:-%{candidate}}
%if 0%{?fedora}
%patch1 -p1 -b.duplicate_struct_iovec
%endif

%build
%cmake -DSUPPORT_SYSTEMD=ON %{?without_glfs} %{?without_rbd} .
make %{?_smp_mflags}
gzip --stdout tcmu-runner.8 > tcmu-runner.8.gz

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_mandir}/man8/
install -m 644 tcmu-runner.8.gz %{buildroot}%{_mandir}/man8/
# install the headers for libtcmu-devel manually
mkdir -p %{buildroot}%{_includedir}
install -m 644 libtcmu.h %{buildroot}%{_includedir}/libtcmu.h
install -m 644 libtcmu_common.h %{buildroot}%{_includedir}/libtcmu_common.h
install -m 644 tcmu-runner.h %{buildroot}%{_includedir}/tcmu-runner.h

%post -n libtcmu -p /sbin/ldconfig

%postun -n libtcmu -p /sbin/ldconfig

%files
%{_bindir}/tcmu-runner
%dir %{_libdir}/tcmu-runner
%{_libdir}/tcmu-runner/handler_qcow.so
%{_sysconfdir}/tcmu
%{_sysconfdir}/dbus-1/system.d/tcmu-runner.conf
%{_datarootdir}/dbus-1/system-services/org.kernel.TCMUService1.service
%{_unitdir}/tcmu-runner.service
%doc README.md
%license LICENSE
%{_mandir}/man8/tcmu-runner.8.gz

%if 0%{!?without_glfs:1}
%files handler-glfs
%{_libdir}/tcmu-runner/handler_glfs.so
%endif

%if 0%{!?without_rbd:1}
%files handler-rbd
%{_libdir}/tcmu-runner/handler_rbd.so
%endif

%files -n libtcmu
%{_libdir}/*.so.*

%files -n libtcmu-devel
%{_includedir}/libtcmu.h
%{_includedir}/libtcmu_common.h
%{_includedir}/tcmu-runner.h
%{_libdir}/*.so


%changelog
* Wed Dec 20 2017 Niels de Vos <ndevos@redhat.com> - 1.3.0-0.2rc4
- do not build tcmu-runner-handler-rbd

* Tue Nov 21 2017 Niels de Vos <ndevos@redhat.com> - 1.3.0-0.1rc4
- Update to version 1.3.0-rc4
- Place Gluster and Ceph RBD handlers in their own sub-package
- Install header files for libtcmu-devel

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Oct 26 2016 Andy Grover <agrover@redhat.com> - 1.1.3-1
- New upstream version

* Mon Aug 15 2016 Andy Grover <agrover@redhat.com> - 1.1.1-1
- New upstream version
- include tcmu-runner.h in -devel

* Wed Aug 3 2016 Andy Grover <agrover@redhat.com> - 1.1.0-1
- New upstream version
- Don't install tcmu-synthesizer, it's an example program

* Wed Apr 6 2016 Andy Grover <agrover@redhat.com> - 1.0.4-1
- New upstream version
- Add man page for tcmu-runner

* Wed Mar 30 2016 Andy Grover <agrover@redhat.com> - 1.0.3-1
- New upstream version

* Thu Mar 24 2016 Andy Grover <agrover@redhat.com> - 1.0.2-1
- New upstream version

* Fri Mar 18 2016 Andy Grover <agrover@redhat.com> - 1.0.1-1
- New upstream version

* Mon Mar 7 2016 Andy Grover <agrover@redhat.com> - 1.0.0-1
- New upstream version
- Add libtcmu and libtcmu-devel subpackages

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Oct 14 2015 Andy Grover <agrover@redhat.com> - 0.9.2-1
- New upstream version

* Tue Oct 13 2015 Andy Grover <agrover@redhat.com> - 0.9.1-1
- Initial Fedora packaging
