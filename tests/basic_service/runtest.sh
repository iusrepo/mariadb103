#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of basic_service
#   Description: The very basic service testing
#   Author: Michal Schorm <mschorm@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2018 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh || exit 1
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE="mariadb"

rlJournalStart
    rlPhaseStartSetup
        rlAssertRpm $PACKAGE
        rlRun "TmpDir=\$(mktemp -d)" 0 "Creating tmp directory"
        rlRun "systemctl stop mariadb"
        rlRun "pushd $TmpDir"
    rlPhaseEnd



    rlPhaseStartTest
        rlRun "systemctl -q status mariadb" 3 "Test status of dead service"
        rlRun "systemctl -q start mariadb" 0 "Start mariadb service"
        rlRun "systemctl -q status mariadb" 0 "Test status of running mariadb service"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "systemctl -q restart mariadb" 0 "Restart running mariadb service"
        rlRun "systemctl -q status mariadb" 0 "Test status of running mariadb service"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "systemctl -q stop mariadb" 0 "Stop mariadb service"
        rlRun "systemctl -q status mariadb" 3 "Test status of dead mariadb service"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "systemctl -q start mariadb" 0 "Start mariadb service"
        rlRun "systemctl -q status mariadb" 0 "Test status of running mariadb service"
    rlPhaseEnd



    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
