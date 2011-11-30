%define _varlogdir      %{_localstatedir}/log/smsd
%define _varrundir      %{_localstatedir}/run/smsd

Name:           smstools
Version:        3.1.14
Release:        2%{?dist}
Summary:        Tools to send and receive short messages through GSM modems or mobile phones

License:        GPLv2+
Group:          Applications/Communications
URL:            http://smstools3.kekekasvi.com
Source0:        http://smstools3.kekekasvi.com/packages/smstools3-%{version}.tar.gz
Source1 :       smsd.init
Source2:        smsd.logrotate
Patch0:		smstools3-3.1.5-loglocation.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service
Requires(pre): shadow-utils

%description
The SMS Server Tools are made to send and receive short messages through
GSM modems. It supports easy file interfaces and it can run external
programs for automatic actions. 

%prep
%setup -q -n smstools3
%patch0 -p1 -b .loglocation
mv doc manual
mv examples/.procmailrc examples/procmailrc
mv examples/.qmailrc examples/qmailrc
find scripts/ examples/ manual/ -type f -print0 |xargs -0 chmod 644

%build
%make -C src 'CFLAGS=%{optflags} -DNOSTATS -D NUMBER_OF_MODEMS=64'

%install
install -Dm 755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/smsd
install -Dm 664 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/smstools
install -Dm 600 examples/smsd.conf.easy $RPM_BUILD_ROOT%{_sysconfdir}/smsd.conf
install -Dm 755 src/smsd %{buildroot}%{_sbindir}/smsd
install -Dm 755 scripts/sendsms %{buildroot}%{_bindir}/smssend
install -Dm 755 scripts/sms2html %{buildroot}%{_bindir}/sms2html
install -Dm 755 scripts/sms2unicode %{buildroot}%{_bindir}/sms2unicode
install -Dm 755 scripts/sms2xml %{buildroot}%{_bindir}/sms2xml
install -Dm 755 scripts/unicode2sms %{buildroot}%{_bindir}/unicode2sms
install -dm 750 %{buildroot}%{_localstatedir}/spool/sms/checked
install -dm 750 %{buildroot}%{_localstatedir}/spool/sms/failed
install -dm 750 %{buildroot}/%{_localstatedir}/spool/sms/incoming
install -dm 770 %{buildroot}/%{_localstatedir}/spool/sms/outgoing
install -dm 750 %{buildroot}/%{_localstatedir}/spool/sms/sent
mkdir -p %{buildroot}/%{_varlogdir}
mkdir -p %{buildroot}/%{_varlogdir}/smsd_stats
mkdir -p %{buildroot}/%{_varrundir}

# Create ghost files
for n in smsd.log smsd_trouble.log; do
    touch %{buildroot}/%{_varlogdir}/$n
done

%pre
getent group smstools >/dev/null || groupadd -r smstools

# on older releases we need to use uucp (here it seems only the uucp group exists)
# on newer releases it's dialout (here it seems both groups exist)
# it would be more elegant to base my if clause on the udev rules instead of the group existence
if [ `getent group dialout` ]
  then
    getent passwd smstools >/dev/null || useradd -r -d /var/lib/smstools -m -g smstools -G dialout smstools
  else
    getent passwd smstools >/dev/null || useradd -r -d /var/lib/smstools -m -g smstools -G uucp smstools
fi


%post
if [ $1 -eq 0 ]; then
        /sbin/chkconfig --add smsd
fi

# Create initial log files so that logrotate doesn't complain
for n in smsd.log smsd_trouble.log; do
        [ -f %{_varlogdir}/$n ] || touch %{_varlogdir}/$n
        chown smstools:smstools %{_varlogdir}/$n
        chmod 640 %{_varlogdir}/$n
done

%preun
if [ $1 -eq 0 ]; then
        /sbin/service smsd stop >/dev/null 2>&1
        /sbin/chkconfig --del smsd
fi

%postun
if [ $1 -ge 1 ]; then
        /sbin/service smsd condrestart >/dev/null 2>&1
fi

%files
%defattr(-,root,root,-)
%doc LICENSE manual/ examples/ scripts/checkhandler-utf-8 scripts/email2sms scripts/eventhandler-utf-8
%doc scripts/mysmsd scripts/regular_run scripts/smsevent scripts/smsresend scripts/sql_demo
%{_sbindir}/*
%{_bindir}/*
%{_initrddir}/smsd
%config(noreplace) %{_sysconfdir}/logrotate.d/smstools
%config(noreplace) %{_sysconfdir}/smsd.conf
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/checked
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/failed
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/incoming
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/outgoing
%attr(-,smstools,smstools) %dir %{_localstatedir}/spool/sms/sent
%attr(0750,smstools,smstools) %dir %{_varlogdir}
%attr(0640,smstools,smstools) %ghost %{_varlogdir}/smsd.log
%attr(0640,smstools,smstools) %ghost %{_varlogdir}/smsd_trouble.log
%attr(0750,smstools,smstools) %dir %{_varlogdir}/smsd_stats
%attr(0700,smstools,smstools) %dir %{_varrundir}
