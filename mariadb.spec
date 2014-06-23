# In f20+ use unversioned docdirs, otherwise the old versioned one
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

# TokuDB engine is now part of MariaDB, but it is available only for x86_64;
# variable tokudb allows to build with TokuDB storage engine
%bcond_with tokudb

Name: mariadb
Version: 10.0.12
Release: 2%{?dist}
Epoch: 1

Summary: A community developed branch of MySQL
Group: Applications/Databases
URL: http://mariadb.org
# Exceptions allow client libraries to be linked with most open source SW,
# not only GPL code.  See README.mysql-license
# Some innobase code from Percona and Google is under BSD license
# Some code related to test-suite is under LGPLv2
License: GPLv2 with exceptions and LGPLv2 and BSD

# The evr of mysql we want to obsolete
%global obsoleted_mysql_evr 5.6-0
%global obsoleted_mysql_case_evr 5.5.30-5

# Regression tests take a long time, you can skip 'em with this
%{!?runselftest:%global runselftest 1}

# When replacing mysql by mariadb these packages are not upated, but rather
# installed and uninstalled. Thus we loose information about mysqld service
# enablement. To address this we use a file to store that information within
# the transaction. Basically the file is created when mysqld is enabled in
# the beginning of the transaction and mysqld is enabled again in the end
# of the transaction in case this flag file exists.
%global mysqld_enabled_flag_file %{_localstatedir}/lib/rpm-state/mysqld_enabled
%global mysqld_running_flag_file %{_localstatedir}/lib/rpm-state/mysqld_running

Source0: http://mirrors.syringanetworks.net/mariadb/mariadb-%{version}/source/mariadb-%{version}.tar.gz
Source3: my.cnf
Source5: my_config.h
Source6: README.mysql-docs
Source7: README.mysql-license
Source8: libmysql.version
Source9: mysql-embedded-check.c
Source10: mariadb.tmpfiles.d
Source11: mariadb.service
Source12: mariadb-prepare-db-dir
Source13: mariadb-wait-ready
Source14: mariadb-check-socket
Source15: mariadb-scripts-common
Source16: mysqld.service
Source50: rh-skipped-tests-base.list
Source51: rh-skipped-tests-intel.list
Source52: rh-skipped-tests-arm.list
Source53: rh-skipped-tests-ppc-s390.list
Source54: rh-skipped-tests-ppc64le.list
# Working around perl dependency checking bug in rpm FTTB. Remove later.
Source999: filter-requires-mysql.sh

# Comments for these patches are in the patch files.
Patch1: mariadb-errno.patch
Patch2: mariadb-strmov.patch
Patch3: mariadb-install-test.patch
Patch4: mariadb-s390-tsc.patch
Patch5: mariadb-logrotate.patch
Patch6: mariadb-cipherspec.patch
Patch7: mariadb-file-contents.patch
Patch8: mariadb-string-overflow.patch
Patch9: mariadb-dh1024.patch
Patch10: mariadb-basedir.patch
Patch11: mariadb-covscan-signexpr.patch
Patch12: mariadb-covscan-stroverflow.patch
Patch13: mariadb-config.patch
Patch14: mariadb-ssltest.patch
Patch15: mariadb-mysql_config.patch

BuildRequires: perl, readline-devel, openssl-devel
BuildRequires: cmake, ncurses-devel, zlib-devel, libaio-devel
BuildRequires: systemd, systemtap-sdt-devel
# make test requires time and ps
BuildRequires: time procps
# auth_pam.so plugin will be build if pam-devel is installed
BuildRequires: pam-devel
# perl modules needed to run regression tests
BuildRequires: perl(Socket), perl(Time::HiRes)
BuildRequires: perl(Data::Dumper), perl(Test::More), perl(Env)

Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: grep, fileutils, bash
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%{?systemd_requires: %systemd_requires}

# MySQL (with caps) is upstream's spelling of their own RPMs for mysql
Obsoletes: MySQL < %{obsoleted_mysql_case_evr}
Conflicts: community-mysql
# MariaDB replaces mysql packages
Provides: mysql = %{epoch}:%{version}-%{release}
Provides: mysql%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: mysql < %{obsoleted_mysql_evr}
# mysql-cluster used to be built from this SRPM, but no more
Obsoletes: mysql-cluster < 5.1.44
 
# When rpm 4.9 is universal, this could be cleaned up:
%global __perl_requires %{SOURCE999}
%global __perllib_requires %{SOURCE999}

# By default, patch(1) creates backup files when chunks apply with offsets.
# Turn that off to ensure such files don't get included in RPMs (cf bz#884755).
%global _default_patch_flags --no-backup-if-mismatch

%description
MariaDB is a community developed branch of MySQL.
MariaDB is a multi-user, multi-threaded SQL database server.
It is a client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. The base package
contains the standard MariaDB/MySQL client programs and generic MySQL files.

%package libs

Summary: The shared libraries required for MariaDB/MySQL clients
Group: Applications/Databases
Requires: /sbin/ldconfig
Provides: mysql-libs = %{epoch}:%{version}-%{release}
Provides: mysql-libs%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: MySQL-libs < %{obsoleted_mysql_case_evr}
Obsoletes: mysql-libs < %{obsoleted_mysql_evr}

%description libs
The mariadb-libs package provides the essential shared libraries for any 
MariaDB/MySQL client program or interface. You will need to install this
package to use any other MariaDB package or any clients that need to connect
to a MariaDB/MySQL server. MariaDB is a community developed branch of MySQL.

%package server

Summary: The MariaDB server and related files
Group: Applications/Databases
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: sh-utils
Requires(pre): /usr/sbin/useradd
# We require this to be present for %%{_tmpfilesdir}
Requires: systemd
# Make sure it's there when scriptlets run, too
Requires(pre): systemd
Requires(post): systemd %{_sbindir}/update-alternatives
Requires(preun): systemd
Requires(postun): systemd %{_sbindir}/update-alternatives
Requires(posttrans): systemd
# mysqlhotcopy needs DBI/DBD support
Requires: perl-DBI, perl-DBD-MySQL
Provides: mysql-server = %{epoch}:%{version}-%{release}
Provides: mysql-server%{?_isa} = %{epoch}:%{version}-%{release}
Provides: mysql-compat-server = %{epoch}:%{version}-%{release}
Provides: mysql-compat-server%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: MySQL-server < %{obsoleted_mysql_case_evr}
Conflicts: community-mysql-server
Obsoletes: mysql-server < %{obsoleted_mysql_evr}

%description server
MariaDB is a multi-user, multi-threaded SQL database server. It is a
client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. This package contains
the MariaDB server and some accompanying files and directories.
MariaDB is a community developed branch of MySQL.

%package devel

Summary: Files for development of MariaDB/MySQL applications
Group: Applications/Databases
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openssl-devel%{?_isa}
Provides: mysql-devel = %{epoch}:%{version}-%{release}
Provides: mysql-devel%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: MySQL-devel < %{obsoleted_mysql_case_evr}
Conflicts: community-mysql-devel
Obsoletes: mysql-devel < %{obsoleted_mysql_evr}

%description devel
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains the libraries and header files that are needed for
developing MariaDB/MySQL client applications.
MariaDB is a community developed branch of MySQL.

%package embedded

Summary: MariaDB as an embeddable library
Group: Applications/Databases
Requires: /sbin/ldconfig
Provides: mysql-embedded = %{epoch}:%{version}-%{release}
Provides: mysql-embedded%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: MySQL-embedded < %{obsoleted_mysql_case_evr}
Obsoletes: mysql-embedded < %{obsoleted_mysql_evr}

%description embedded
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains a version of the MariaDB server that can be embedded
into a client application instead of running as a separate process.
MariaDB is a community developed branch of MySQL.

%package embedded-devel

Summary: Development files for MariaDB as an embeddable library
Group: Applications/Databases
Requires: %{name}-embedded%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-devel%{?_isa} = %{epoch}:%{version}-%{release}
Provides: mysql-embedded-devel = %{epoch}:%{version}-%{release}
Provides: mysql-embedded-devel%{?_isa} = %{epoch}:%{version}-%{release}
Conflicts: community-mysql-embedded-devel
Obsoletes: MySQL-embedded-devel < %{obsoleted_mysql_case_evr}
Obsoletes: mysql-embedded-devel < %{obsoleted_mysql_evr}

%description embedded-devel
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains files needed for developing and testing with
the embedded version of the MariaDB server.
MariaDB is a community developed branch of MySQL.

%package bench

Summary: MariaDB benchmark scripts and data
Group: Applications/Databases
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Provides: mysql-bench = %{epoch}:%{version}-%{release}
Provides: mysql-bench%{?_isa} = %{epoch}:%{version}-%{release}
Conflicts: community-mysql-bench
Obsoletes: MySQL-bench < %{obsoleted_mysql_case_evr}
Obsoletes: mysql-bench < %{obsoleted_mysql_evr}

%description bench
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains benchmark scripts and data for use when benchmarking
MariaDB.
MariaDB is a community developed branch of MySQL.

%package test

Summary: The test suite distributed with MariaD
Group: Applications/Databases
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-server%{?_isa} = %{epoch}:%{version}-%{release}
Provides: mysql-test = %{epoch}:%{version}-%{release}
Provides: mysql-test%{?_isa} = %{epoch}:%{version}-%{release}
Conflicts: community-mysql-test
Obsoletes: MySQL-test < %{obsoleted_mysql_case_evr}
Obsoletes: mysql-test < %{obsoleted_mysql_evr}
Requires: perl(Socket), perl(Time::HiRes)
Requires: perl(Data::Dumper), perl(Test::More), perl(Env)

%description test
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains the regression test suite distributed with
the MariaDB sources.
MariaDB is a community developed branch of MySQL.

%prep
%setup -q -n mariadb-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1

# workaround for upstream bug #56342
rm -f mysql-test/t/ssl_8k_key-master.opt

# generate a list of tests that fail, but are not disabled by upstream
cat %{SOURCE50} > mysql-test/rh-skipped-tests.list

# disable some tests failing on different architectures
%ifarch x86_64 i686
cat %{SOURCE51} >> mysql-test/rh-skipped-tests.list
%endif

%ifarch %{arm} aarch64
cat %{SOURCE52} >> mysql-test/rh-skipped-tests.list
%endif

%ifarch ppc ppc64 ppc64p7 s390 s390x
cat %{SOURCE53} >> mysql-test/rh-skipped-tests.list
%endif

%ifarch ppc64le
cat %{SOURCE54} >> mysql-test/rh-skipped-tests.list
%endif


%build

# fail quickly and obviously if user tries to build as root
%if %runselftest
	if [ x"`id -u`" = x0 ]; then
		echo "mariadb's regression tests fail if run as root."
		echo "If you really need to build the RPM as root, use"
		echo "--define='runselftest 0' to skip the regression tests."
		exit 1
	fi
%endif

CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE"
# force PIC mode so that we can build libmysqld.so
CFLAGS="$CFLAGS -fPIC"
# GCC 4.9 causes segfaults: https://mariadb.atlassian.net/browse/MDEV-6360
CFLAGS="$CFLAGS -fno-delete-null-pointer-checks"
# gcc seems to have some bugs on sparc as of 4.4.1, back off optimization
# submitted as bz #529298
%ifarch sparc sparcv9 sparc64
CFLAGS=`echo $CFLAGS| sed -e "s|-O2|-O1|g" `
%endif
# significant performance gains can be achieved by compiling with -O3 optimization
# rhbz#1051069
%ifarch ppc64
CFLAGS=`echo $CFLAGS| sed -e "s|-O2|-O3|g" `
%endif
CXXFLAGS="$CFLAGS"
export CFLAGS CXXFLAGS
# building with PIE
LDFLAGS="$LDFLAGS -pie"
export LDFLAGS

# The INSTALL_xxx macros have to be specified relative to CMAKE_INSTALL_PREFIX
# so we can't use %%{_datadir} and so forth here.

cmake . -DBUILD_CONFIG=mysql_release \
	-DFEATURE_SET="community" \
	-DINSTALL_LAYOUT=RPM \
	-DRPM="%{?rhel:rhel%{rhel}}%{!?rhel:fedora%{fedora}}" \
	-DCMAKE_INSTALL_PREFIX="%{_prefix}" \
%if 0%{?fedora} >= 20
	-DINSTALL_DOCDIR=share/doc/%{name} \
	-DINSTALL_DOCREADMEDIR=share/doc/%{name} \
%else
	-DINSTALL_DOCDIR=share/doc/%{name}-%{version} \
	-DINSTALL_DOCREADMEDIR=share/doc/%{name}-%{version} \
%endif
	-DINSTALL_INCLUDEDIR=include/mysql \
	-DINSTALL_INFODIR=share/info \
	-DINSTALL_LIBDIR="%{_lib}/mysql" \
	-DINSTALL_MANDIR=share/man \
	-DINSTALL_MYSQLSHAREDIR=share/%{name} \
	-DINSTALL_MYSQLTESTDIR=share/mysql-test \
	-DINSTALL_PLUGINDIR="%{_lib}/mysql/plugin" \
	-DINSTALL_SBINDIR=libexec \
	-DINSTALL_SCRIPTDIR=bin \
	-DINSTALL_SQLBENCHDIR=share \
	-DINSTALL_SUPPORTFILESDIR=share/%{name} \
	-DMYSQL_DATADIR="%{_localstatedir}/lib/mysql" \
	-DMYSQL_UNIX_ADDR="%{_localstatedir}/lib/mysql/mysql.sock" \
	-DENABLED_LOCAL_INFILE=ON \
	-DENABLE_DTRACE=ON \
	-DWITH_EMBEDDED_SERVER=ON \
	-DWITH_READLINE=ON \
	-DWITH_SSL=system \
	-DWITH_ZLIB=system \
	-DWITH_PCRE=system \
	-DWITH_JEMALLOC=no \
%{!?with_tokudb:	-DWITHOUT_TOKUDB=ON}\
	-DTMPDIR=%{_localstatedir}/tmp \
	-DWITH_MYSQLD_LDFLAGS="-Wl,-z,relro,-z,now"

make %{?_smp_mflags} VERBOSE=1

# debuginfo extraction scripts fail to find source files in their real
# location -- satisfy them by copying these files into location, which
# is expected by scripts
for e in innobase xtradb ; do
  for f in pars0grm.y pars0lex.l ; do
    cp -p "storage/$e/pars/$f" "storage/$e/$f"
  done
done

%check
%if %runselftest
  # hack to let 32- and 64-bit tests run concurrently on same build machine
  case `uname -m` in
    ppc64 | ppc64p7 | s390x | x86_64 | sparc64 )
      MTR_BUILD_THREAD=7
      ;;
    *)
      MTR_BUILD_THREAD=11
      ;;
  esac
  export MTR_BUILD_THREAD
  export MTR_PARALLEL=1

  make test VERBOSE=1

  # The cmake build scripts don't provide any simple way to control the
  # options for mysql-test-run, so ignore the make target and just call it
  # manually.  Nonstandard options chosen are:
  # --force to continue tests after a failure
  # no retries please
  # test SSL with --ssl
  # skip tests that are listed in rh-skipped-tests.list
  # avoid redundant test runs with --binlog-format=mixed
  # increase timeouts to prevent unwanted failures during mass rebuilds
  (
    cd mysql-test
    perl ./mysql-test-run.pl --force --retry=0 --ssl \
	--skip-test-list=rh-skipped-tests.list \
	--suite-timeout=720 --testcase-timeout=30 \
	--mysqld=--binlog-format=mixed --force-restart \
	--shutdown-timeout=60 --max-test-fail=0
    # cmake build scripts will install the var cruft if left alone :-(
    rm -rf var
  )
%endif

%install
make DESTDIR=$RPM_BUILD_ROOT install

# List the installed tree for RPM package maintenance purposes.
find $RPM_BUILD_ROOT -print | sed "s|^$RPM_BUILD_ROOT||" | sort > ROOTFILES

# multilib header hacks
# we only apply this to known Red Hat multilib arches, per bug #181335
case `uname -i` in
  i386 | x86_64 | ppc | ppc64 | ppc64p7 | s390 | s390x | sparc | sparc64 | aarch64 )
    mv $RPM_BUILD_ROOT%{_includedir}/mysql/my_config.h $RPM_BUILD_ROOT%{_includedir}/mysql/my_config_`uname -i`.h
    mv $RPM_BUILD_ROOT%{_includedir}/mysql/private/config.h $RPM_BUILD_ROOT%{_includedir}/mysql/private/my_config_`uname -i`.h
    install -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_includedir}/mysql/
    install -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_includedir}/mysql/private/config.h
    ;;
  arm* )
    mv $RPM_BUILD_ROOT%{_includedir}/mysql/my_config.h $RPM_BUILD_ROOT%{_includedir}/mysql/my_config_arm.h
    mv $RPM_BUILD_ROOT%{_includedir}/mysql/private/config.h $RPM_BUILD_ROOT%{_includedir}/mysql/private/my_config_arm.h
    install -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_includedir}/mysql/
    install -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_includedir}/mysql/private/config.h
    ;;
  *)
    ;;
esac

# cmake generates some completely wacko references to -lprobes_mysql when
# building with dtrace support.  Haven't found where to shut that off,
# so resort to this blunt instrument.  While at it, let's not reference
# libmysqlclient_r anymore either.
sed -e 's/-lprobes_mysql//' -e 's/-lmysqlclient_r/-lmysqlclient/' \
	${RPM_BUILD_ROOT}%{_bindir}/mysql_config >mysql_config.tmp
cp -p -f mysql_config.tmp ${RPM_BUILD_ROOT}%{_bindir}/mysql_config
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/mysql_config

# install INFO_SRC, INFO_BIN into libdir (upstream thinks these are doc files,
# but that's pretty wacko --- see also mariadb-file-contents.patch)
mv ${RPM_BUILD_ROOT}%{_pkgdocdir}/MariaDB-server-%{version}/INFO_SRC ${RPM_BUILD_ROOT}%{_libdir}/mysql/
mv ${RPM_BUILD_ROOT}%{_pkgdocdir}/MariaDB-server-%{version}/INFO_BIN ${RPM_BUILD_ROOT}%{_libdir}/mysql/
rm -rf ${RPM_BUILD_ROOT}%{_pkgdocdir}/MariaDB-server-%{version}/

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
chmod 0750 $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}/%{name}.log
ln -s %{_localstatedir}/log/%{name}/%{name}.log $RPM_BUILD_ROOT%{_localstatedir}/log/mysqld.log

# current setting in my.cnf is to use /var/run/mariadb for creating pid file,
# however since my.cnf is not updated by RPM if changed, we need to create mysqld
# as well because users can have od settings in their /etc/my.cnf
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/mysqld
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/%{name}
install -m 0755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/mysql

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
install -p -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/my.cnf

# install systemd unit files and scripts for handling server startup
mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}
install -p -m 644 %{SOURCE11} ${RPM_BUILD_ROOT}%{_unitdir}/
install -p -m 644 %{SOURCE16} ${RPM_BUILD_ROOT}%{_unitdir}/`basename %{SOURCE16}`
install -p -m 755 %{SOURCE12} ${RPM_BUILD_ROOT}%{_libexecdir}/
install -p -m 755 %{SOURCE13} ${RPM_BUILD_ROOT}%{_libexecdir}/
install -p -m 755 %{SOURCE14} ${RPM_BUILD_ROOT}%{_libexecdir}/
install -p -m 644 %{SOURCE15} ${RPM_BUILD_ROOT}%{_libexecdir}/

mkdir -p $RPM_BUILD_ROOT%{_tmpfilesdir}
install -p -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_tmpfilesdir}/%{name}.conf

# Fix scripts for multilib safety
mv ${RPM_BUILD_ROOT}%{_bindir}/mysql_config ${RPM_BUILD_ROOT}%{_libdir}/mysql/mysql_config
touch ${RPM_BUILD_ROOT}%{_bindir}/mysql_config

mv ${RPM_BUILD_ROOT}%{_bindir}/mysqlbug ${RPM_BUILD_ROOT}%{_libdir}/mysql/mysqlbug
touch ${RPM_BUILD_ROOT}%{_bindir}/mysqlbug

# Remove libmysqld.a
rm -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqld.a

# libmysqlclient_r is no more.  Upstream tries to replace it with symlinks
# but that really doesn't work (wrong soname in particular).  We'll keep
# just the devel libmysqlclient_r.so link, so that rebuilding without any
# source change is enough to get rid of dependency on libmysqlclient_r.
rm -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqlclient_r.so*
ln -s libmysqlclient.so ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqlclient_r.so

# mysql-test includes one executable that doesn't belong under /usr/share,
# so move it and provide a symlink
mv ${RPM_BUILD_ROOT}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process ${RPM_BUILD_ROOT}%{_bindir}
ln -s ../../../../../bin/my_safe_process ${RPM_BUILD_ROOT}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process

# should move this to /etc/ ?
rm -f ${RPM_BUILD_ROOT}%{_bindir}/mysql_embedded
rm -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/*.a
rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{name}/binary-configure
rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{name}/magic
rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{name}/ndb-config-2-node.ini
rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{name}/mysql.server
rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{name}/mysqld_multi.server
rm -f ${RPM_BUILD_ROOT}%{_mandir}/man1/mysql-stress-test.pl.1*
rm -f ${RPM_BUILD_ROOT}%{_mandir}/man1/mysql-test-run.pl.1*
rm -f ${RPM_BUILD_ROOT}%{_bindir}/mytop

# put logrotate script where it needs to be
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mv ${RPM_BUILD_ROOT}%{_datadir}/%{name}/mysql-log-rotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/mysql" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

# copy additional docs into build tree so %%doc will find them
cp -p %{SOURCE6} README.mysql-docs
cp -p %{SOURCE7} README.mysql-license

# install the list of skipped tests to be available for user runs
install -p -m 0644 mysql-test/rh-skipped-tests.list ${RPM_BUILD_ROOT}%{_datadir}/mysql-test

# remove unneeded RHEL-4 SELinux stuff
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{name}/SELinux/

# remove SysV init script
rm -f ${RPM_BUILD_ROOT}%{_sysconfdir}/init.d/mysql

# remove duplicate logrotate script
rm -f ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/mysql

# remove solaris files
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{name}/solaris/

%post devel
%{_sbindir}/update-alternatives --install %{_bindir}/mysql_config \
	mysql_config %{_libdir}/mysql/mysql_config %{__isa_bits}

%pre server
/usr/sbin/groupadd -g 27 -o -r mysql >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g mysql -o -r -d %{_localstatedir}/lib/mysql -s /sbin/nologin \
	-c "MariaDB Server" -u 27 mysql >/dev/null 2>&1 || :

# Explicitly enable mysqld if it was enabled in the beggining
# of the transaction. Otherwise mysqld is disabled always when
# replacing mysql with mariadb, because it is not recognized
# as updating, but rather as removal and install.
if /bin/systemctl is-enabled mysqld.service >/dev/null 2>&1 ; then
    touch %mysqld_enabled_flag_file >/dev/null 2>&1 || :
fi

# Since mysqld.service became a symlink to mariadb.service, turning off
# the running mysqld service doesn't work fine (BZ#1002996). As a work-around
# we explicitly stop mysqld before upgrade and start after it again.
if [ ! -L %{_unitdir}/mysqld.service ] && /bin/systemctl is-active mysqld.service &>/dev/null ; then
    touch %mysqld_running_flag_file >/dev/null 2>&1 || :
    /bin/systemctl stop mysqld.service >/dev/null 2>&1 || :
fi

%posttrans server
if [ -f %mysqld_enabled_flag_file ] ; then
    /bin/systemctl enable %{name}.service >/dev/null 2>&1 || :
    rm -f %mysqld_enabled_flag_file >/dev/null 2>&1 || :
fi
if [ -f %mysqld_running_flag_file ] ; then
    /bin/systemctl start %{name}.service >/dev/null 2>&1 || :
    rm -f %mysqld_running_flag_file >/dev/null 2>&1 || :
fi


%post libs -p /sbin/ldconfig

%post server
%systemd_post %{name}.service
/bin/chmod 0755 %{_localstatedir}/lib/mysql

%{_sbindir}/update-alternatives --install %{_bindir}/mysqlbug \
	mysqlbug %{_libdir}/mysql/mysqlbug %{__isa_bits}

%post embedded -p /sbin/ldconfig

%postun devel
if [ $1 -eq 0 ] ; then
    %{_sbindir}/update-alternatives --remove mysql_config %{_libdir}/mysql/mysql_config
fi

%preun server
%systemd_preun %{name}.service

%postun libs -p /sbin/ldconfig

%postun server
%systemd_postun_with_restart %{name}.service
if [ $1 -eq 0 ] ; then
    %{_sbindir}/update-alternatives --remove mysqlbug %{_libdir}/mysql/mysqlbug
fi

%postun embedded -p /sbin/ldconfig

%files
%doc README COPYING COPYING.LESSER README.mysql-license
%doc storage/innobase/COPYING.Percona storage/innobase/COPYING.Google
%doc README.mysql-docs

%{_bindir}/msql2mysql
%{_bindir}/mysql
%{_bindir}/mysql_find_rows
%{_bindir}/mysql_waitpid
%{_bindir}/mysqlaccess
%{_bindir}/mysqladmin
%{_bindir}/mysqlbinlog
%{_bindir}/mysqlcheck
%{_bindir}/mysqldump
%{?with_tokudb:%{_bindir}/tokuftdump}
%{_bindir}/mysqlimport
%{_bindir}/mysqlshow
%{_bindir}/mysqlslap
%{_bindir}/my_print_defaults
%{_bindir}/aria_chk
%{_bindir}/aria_dump_log
%{_bindir}/aria_ftdump
%{_bindir}/aria_pack
%{_bindir}/aria_read_log

%{_mandir}/man1/mysql.1*
%{_mandir}/man1/mysql_find_rows.1*
%{_mandir}/man1/mysql_waitpid.1*
%{_mandir}/man1/mysqlaccess.1*
%{_mandir}/man1/mysqladmin.1*
%{_mandir}/man1/mysqldump.1*
%{_mandir}/man1/mysqlshow.1*
%{_mandir}/man1/mysqlslap.1*
%{_mandir}/man1/my_print_defaults.1*

%config(noreplace) %{_sysconfdir}/my.cnf.d/client.cnf
%config(noreplace) %{_sysconfdir}/my.cnf.d/connect.cnf

%files libs
%doc README COPYING COPYING.LESSER README.mysql-license
%doc storage/innobase/COPYING.Percona storage/innobase/COPYING.Google
# although the default my.cnf contains only server settings, we put it in the
# libs package because it can be used for client settings too.
%config(noreplace) %{_sysconfdir}/my.cnf
%config(noreplace) %{_sysconfdir}/my.cnf.d/mysql-clients.cnf
%dir %{_sysconfdir}/my.cnf.d
%dir %{_libdir}/mysql
%{_libdir}/mysql/libmysqlclient.so.*
%{_sysconfdir}/ld.so.conf.d/*

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/english
%lang(cs) %{_datadir}/%{name}/czech
%lang(da) %{_datadir}/%{name}/danish
%lang(nl) %{_datadir}/%{name}/dutch
%lang(et) %{_datadir}/%{name}/estonian
%lang(fr) %{_datadir}/%{name}/french
%lang(de) %{_datadir}/%{name}/german
%lang(el) %{_datadir}/%{name}/greek
%lang(hu) %{_datadir}/%{name}/hungarian
%lang(it) %{_datadir}/%{name}/italian
%lang(ja) %{_datadir}/%{name}/japanese
%lang(ko) %{_datadir}/%{name}/korean
%lang(no) %{_datadir}/%{name}/norwegian
%lang(no) %{_datadir}/%{name}/norwegian-ny
%lang(pl) %{_datadir}/%{name}/polish
%lang(pt) %{_datadir}/%{name}/portuguese
%lang(ro) %{_datadir}/%{name}/romanian
%lang(ru) %{_datadir}/%{name}/russian
%lang(sr) %{_datadir}/%{name}/serbian
%lang(sk) %{_datadir}/%{name}/slovak
%lang(es) %{_datadir}/%{name}/spanish
%lang(sv) %{_datadir}/%{name}/swedish
%lang(uk) %{_datadir}/%{name}/ukrainian
%{_datadir}/%{name}/charsets

%files server
%doc support-files/*.cnf

%{_bindir}/myisamchk
%{_bindir}/myisam_ftdump
%{_bindir}/myisamlog
%{_bindir}/myisampack
%{_bindir}/mysql_convert_table_format
%{_bindir}/mysql_fix_extensions
%{_bindir}/mysql_install_db
%{_bindir}/mysql_plugin
%{_bindir}/mysql_secure_installation
%{_bindir}/mysql_setpermission
%{_bindir}/mysql_tzinfo_to_sql
%{_bindir}/mysql_upgrade
%{_bindir}/mysql_zap
%ghost %{_bindir}/mysqlbug
%{_bindir}/mysqldumpslow
%{_bindir}/mysqld_multi
%{_bindir}/mysqld_safe
%{_bindir}/mysqlhotcopy
%{_bindir}/mysqltest
%{_bindir}/innochecksum
%{_bindir}/perror
%{_bindir}/replace
%{_bindir}/resolve_stack_dump
%{_bindir}/resolveip

%config(noreplace) %{_sysconfdir}/my.cnf.d/server.cnf
%{?with_tokudb:%config(noreplace) %{_sysconfdir}/my.cnf.d/tokudb.cnf}

%{_libexecdir}/mysqld

%{_libdir}/mysql/INFO_SRC
%{_libdir}/mysql/INFO_BIN

%{_libdir}/mysql/mysqlbug

%{_libdir}/mysql/plugin

%{_mandir}/man1/msql2mysql.1*
%{_mandir}/man1/myisamchk.1*
%{_mandir}/man1/myisamlog.1*
%{_mandir}/man1/myisampack.1*
%{_mandir}/man1/mysql_convert_table_format.1*
%{_mandir}/man1/myisam_ftdump.1*
%{_mandir}/man1/mysql.server.1*
%{_mandir}/man1/mysql_fix_extensions.1*
%{_mandir}/man1/mysql_install_db.1*
%{_mandir}/man1/mysql_plugin.1*
%{_mandir}/man1/mysql_secure_installation.1*
%{_mandir}/man1/mysql_upgrade.1*
%{_mandir}/man1/mysql_zap.1*
%{_mandir}/man1/mysqlbug.1*
%{_mandir}/man1/mysqldumpslow.1*
%{_mandir}/man1/mysqlbinlog.1*
%{_mandir}/man1/mysqlcheck.1*
%{_mandir}/man1/mysqld_multi.1*
%{_mandir}/man1/mysqld_safe.1*
%{_mandir}/man1/mysqlhotcopy.1*
%{_mandir}/man1/mysqlimport.1*
%{_mandir}/man1/mysql_setpermission.1*
%{_mandir}/man1/mysqltest.1*
%{_mandir}/man1/innochecksum.1*
%{_mandir}/man1/perror.1*
%{_mandir}/man1/replace.1*
%{_mandir}/man1/resolve_stack_dump.1*
%{_mandir}/man1/resolveip.1*
%{_mandir}/man1/mysql_tzinfo_to_sql.1*
%{_mandir}/man8/mysqld.8*

%{_datadir}/%{name}/errmsg-utf8.txt
%{_datadir}/%{name}/fill_help_tables.sql
%{_datadir}/%{name}/install_spider.sql
%{_datadir}/%{name}/mysql_system_tables.sql
%{_datadir}/%{name}/mysql_system_tables_data.sql
%{_datadir}/%{name}/mysql_test_data_timezone.sql
%{_datadir}/%{name}/mysql_performance_tables.sql
%{_datadir}/%{name}/my-*.cnf

%{_unitdir}/mysqld.service
%{_unitdir}/%{name}.service
%{_libexecdir}/mariadb-prepare-db-dir
%{_libexecdir}/mariadb-wait-ready
%{_libexecdir}/mariadb-scripts-common
%{_libexecdir}/mariadb-check-socket

%{_tmpfilesdir}/%{name}.conf
%attr(0755,mysql,mysql) %dir %{_localstatedir}/run/mysqld
%attr(0755,mysql,mysql) %dir %{_localstatedir}/run/%{name}
%attr(0755,mysql,mysql) %dir %{_localstatedir}/lib/mysql
%attr(0750,mysql,mysql) %dir %{_localstatedir}/log/%{name}
%attr(0640,mysql,mysql) %config %ghost %verify(not md5 size mtime) %{_localstatedir}/log/%{name}/%{name}.log
                        %config %ghost %verify(not md5 size mtime) %{_localstatedir}/log/mysqld.log
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%files devel
%ghost %{_bindir}/mysql_config
%{_includedir}/mysql
%{_datadir}/aclocal/mysql.m4
%{_libdir}/mysql/libmysqlclient.so
%{_libdir}/mysql/libmysqlclient_r.so
%{_libdir}/mysql/mysql_config
%{_mandir}/man1/mysql_config.1*

%files embedded
%doc README COPYING COPYING.LESSER README.mysql-license
%doc storage/innobase/COPYING.Percona storage/innobase/COPYING.Google
%{_libdir}/mysql/libmysqld.so.*

%files embedded-devel
%{_libdir}/mysql/libmysqld.so
%{_bindir}/mysql_client_test_embedded
%{_bindir}/mysqltest_embedded
%{_mandir}/man1/mysql_client_test_embedded.1*
%{_mandir}/man1/mysqltest_embedded.1*

%files bench
%{_datadir}/sql-bench

%files test
%{_bindir}/mysql_client_test
%{_bindir}/my_safe_process
%attr(-,mysql,mysql) %{_datadir}/mysql-test

%{_mandir}/man1/mysql_client_test.1*

%changelog
* Wed Jun 18 2014 Mikko Tiihonen <mikko.tiihonen@iki.fi> - 1:10.0.12-2
- Use -fno-delete-null-pointer-checks to avoid segfaults with gcc 4.9

* Tue Jun 17 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.12-1
- Rebase to version 10.0.12

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.0.11-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun  3 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.11-4
- rebuild with tests failing on different arches disabled (#1096787)

* Thu May 29 2014 Dan Horák <dan[at]danny.cz> - 1:10.0.11-2
- rebuild with tests failing on big endian arches disabled (#1096787)

* Wed May 14 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.11-1
- Rebase to version 10.0.11

* Mon May 05 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.10-3
- Script for socket check enhanced

* Thu Apr 10 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.10-2
- use system pcre library

* Thu Apr 10 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.10-1
- Rebase to version 10.0.10

* Wed Mar 12 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.36-2
- Server crashes on SQL select containing more group by and left join statements using innodb tables
  Resolves: #1065676
- Fix paths in helper scripts
- Move language files into mariadb directory

* Thu Mar 06 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.36-1
- Rebase to 5.5.36
  https://kb.askmonty.org/en/mariadb-5536-changelog/

* Tue Feb 25 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-5
- Daemon helper scripts sanity changes and spec files clean-up

* Tue Feb 11 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-4
- Fix typo in mysqld.service
  Resolves: #1063981

* Wed Feb  5 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-3
- Do not touch the log file in post script, so it does not get wrong owner
  Resolves: #1061045

* Thu Jan 30 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-1
- Rebase to 5.5.35
  https://kb.askmonty.org/en/mariadb-5535-changelog/
  Also fixes: CVE-2014-0001, CVE-2014-0412, CVE-2014-0437, CVE-2013-5908,
  CVE-2014-0420, CVE-2014-0393, CVE-2013-5891, CVE-2014-0386, CVE-2014-0401,
  CVE-2014-0402
  Resolves: #1054043
  Resolves: #1059546

* Tue Jan 14 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.34-9
- Adopt compatible system versioning
  Related: #1045013
- Use compatibility mysqld.service instead of link
  Related: #1014311

* Mon Jan 13 2014 Rex Dieter <rdieter@fedoraproject.org> 1:5.5.34-8
- move mysql_config alternatives scriptlets to -devel too

* Fri Jan 10 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-7
- Build with -O3 on ppc64
  Related: #1051069
- Move mysql_config to -devel sub-package and remove Require: mariadb
  Related: #1050920

* Fri Jan 10 2014 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 1:5.5.34-6
- Disable main.gis-precise test also for AArch64
- Disable perfschema.func_file_io and perfschema.func_mutex for AArch64
  (like it is done for 32-bit ARM)

* Fri Jan 10 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-5
- Clean all non-needed doc files properly

* Wed Jan  8 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-4
- Read socketfile location in mariadb-prepare-db-dir script

* Mon Jan  6 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-3
- Don't test EDH-RSA-DES-CBC-SHA cipher, it seems to be removed from openssl
  which now makes mariadb/mysql FTBFS because openssl_1 test fails
  Related: #1044565
- Use upstream's layout for symbols version in client library
  Related: #1045013
- Check if socket file is not being used by another process at a time
  of starting the service
  Related: #1045435
- Use %%ghost directive for the log file
  Related: 1043501

* Wed Nov 27 2013 Honza Horak <hhorak@redhat.com> 1:5.5.34-2
- Fix mariadb-wait-ready script

* Fri Nov 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.34-1
- Rebase to 5.5.34

* Mon Nov  4 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-4
- Fix spec file to be ready for backport by Oden Eriksson
  Resolves: #1026404

* Mon Nov  4 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-3
- Add pam-devel to build-requires in order to build
  Related: #1019945
- Check if correct process is running in mysql-wait-ready script
  Related: #1026313

* Mon Oct 14 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-2
- Turn on test suite

* Thu Oct 10 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-1
- Rebase to 5.5.33a
  https://kb.askmonty.org/en/mariadb-5533-changelog/
  https://kb.askmonty.org/en/mariadb-5533a-changelog/
- Enable outfile_loaddata test
- Disable tokudb_innodb_xa_crash test

* Mon Sep  2 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-12
- Re-organize my.cnf to include only generic settings
  Resolves: #1003115
- Move pid file location to /var/run/mariadb
- Make mysqld a symlink to mariadb unit file rather than the opposite way
  Related: #999589

* Thu Aug 29 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-11
- Move log file into /var/log/mariadb/mariadb.log
- Rename logrotate script to mariadb
- Resolves: #999589

* Wed Aug 14 2013 Rex Dieter <rdieter@fedoraproject.org> 1:5.5.32-10
- fix alternatives usage

* Tue Aug 13 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-9
- Multilib issues solved by alternatives
  Resolves: #986959

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 1:5.5.32-8
- Perl 5.18 rebuild

* Wed Jul 31 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-7
- Do not use login shell for mysql user

* Tue Jul 30 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-6
- Remove unneeded systemd-sysv requires
- Provide mysql-compat-server symbol
- Create mariadb.service symlink
- Fix multilib header location for arm
- Enhance documentation in the unit file
- Use scriptstub instead of links to avoid multilib conflicts
- Add condition for doc placement in F20+

* Sun Jul 28 2013 Dennis Gilmore <dennis@ausil.us> - 1:5.5.32-5
- remove "Requires(pretrans): systemd" since its not possible
- when installing mariadb and systemd at the same time. as in a new install

* Sat Jul 27 2013 Kevin Fenzi <kevin@scrye.com> 1:5.5.32-4
- Set rpm doc macro to install docs in unversioned dir

* Fri Jul 26 2013 Dennis Gilmore <dennis@ausil.us> 1:5.5.32-3
- add Requires(pre) on systemd for the server package

* Tue Jul 23 2013 Dennis Gilmore <dennis@ausil.us> 1:5.5.32-2
- replace systemd-units requires with systemd
- remove solaris files

* Fri Jul 19 2013 Honza Horak <hhorak@redhat.com> 1:5.5.32-1
- Rebase to 5.5.32
  https://kb.askmonty.org/en/mariadb-5532-changelog/
- Clean-up un-necessary systemd snippets

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1:5.5.31-7
- Perl 5.18 rebuild

* Mon Jul  1 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-6
- Test suite params enhanced to decrease server condition influence
- Fix misleading error message when uninstalling built-in plugins
  Related: #966873

* Thu Jun 27 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-5
- Apply fixes found by Coverity static analysis tool

* Wed Jun 19 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-4
- Do not use pretrans scriptlet, which doesn't work in anaconda
  Resolves: #975348

* Fri Jun 14 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-3
- Explicitly enable mysqld if it was enabled in the beggining
  of the transaction.

* Thu Jun 13 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-2
- Apply man page fix from Jan Stanek

* Fri May 24 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-1
- Rebase to 5.5.31
  https://kb.askmonty.org/en/mariadb-5531-changelog/
- Preserve time-stamps in case of installed files
- Use /var/tmp instead of /tmp, since the later is using tmpfs,
  which can cause problems
  Resolves: #962087
- Fix test suite requirements

* Sun May  5 2013 Honza Horak <hhorak@redhat.com> 1:5.5.30-2
- Remove mytop utility, which is packaged separately
- Resolve multilib conflicts in mysql/private/config.h

* Fri Mar 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.30-1
- Rebase to 5.5.30
  https://kb.askmonty.org/en/mariadb-5530-changelog/

* Fri Mar 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.29-11
- Obsolete MySQL since it is now renamed to community-mysql
- Remove real- virtual names

* Thu Mar 21 2013 Honza Horak <hhorak@redhat.com> 1:5.5.29-10
- Adding epoch to have higher priority than other mysql implementations
  when comes to provider comparison

* Wed Mar 13 2013 Honza Horak <hhorak@redhat.com> 5.5.29-9
- Let mariadb-embedded-devel conflict with MySQL-embedded-devel
- Adjust mariadb-sortbuffer.patch to correspond with upstream patch

* Mon Mar  4 2013 Honza Horak <hhorak@redhat.com> 5.5.29-8
- Mask expected warnings about setrlimit in test suite

* Thu Feb 28 2013 Honza Horak <hhorak@redhat.com> 5.5.29-7
- Use configured prefix value instead of guessing basedir
  in mysql_config
Resolves: #916189
- Export dynamic columns and non-blocking API functions documented
  by upstream

* Wed Feb 27 2013 Honza Horak <hhorak@redhat.com> 5.5.29-6
- Fix sort_buffer_length option type

* Wed Feb 13 2013 Honza Horak <hhorak@redhat.com> 5.5.29-5
- Suppress warnings in tests and skip tests also on ppc64p7

* Tue Feb 12 2013 Honza Horak <hhorak@redhat.com> 5.5.29-4
- Suppress warning in tests on ppc
- Enable fixed index_merge_myisam test case

* Thu Feb 07 2013 Honza Horak <hhorak@redhat.com> 5.5.29-3
- Packages need to provide also %%_isa version of mysql package
- Provide own symbols with real- prefix to distinguish from mysql
  unambiguously
- Fix format for buffer size in error messages (MDEV-4156)
- Disable some tests that fail on ppc and s390
- Conflict only with real-mysql, otherwise mariadb conflicts with ourself

* Tue Feb 05 2013 Honza Horak <hhorak@redhat.com> 5.5.29-2
- Let mariadb-libs to own /etc/my.cnf.d

* Thu Jan 31 2013 Honza Horak <hhorak@redhat.com> 5.5.29-1
- Rebase to 5.5.29
  https://kb.askmonty.org/en/mariadb-5529-changelog/
- Fix inaccurate default for socket location in mysqld-wait-ready
  Resolves: #890535

* Thu Jan 31 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-8
- Enable obsoleting mysql

* Wed Jan 30 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-7
- Adding necessary hacks for perl dependency checking, rpm is still
  not wise enough
- Namespace sanity re-added for symbol default_charset_info

* Mon Jan 28 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-6
- Removed %%{_isa} from provides/obsoletes, which doesn't allow
  proper obsoleting
- Do not obsolete mysql at the time of testing

* Thu Jan 10 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-5
- Added licenses LGPLv2 and BSD
- Removed wrong usage of %%{epoch}
- Test-suite is run in %%check
- Removed perl dependency checking adjustment, rpm seems to be smart enough
- Other minor spec file fixes

* Tue Dec 18 2012 Honza Horak <hhorak@redhat.com> 5.5.28a-4
- Packaging of MariaDB based on MySQL package

