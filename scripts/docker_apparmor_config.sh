#!/usr/bin/env bash

# requires sudo and apparmor-utils
#
# > sudo apt install apparmor-utils
#

set -euo pipefail

script_dir=$(dirname $0)
policy=${script_dir}/docker-allow-dbus.apparmor.policy

# Use docker built in security options to load custom template
# add custom apparmor policy
cp ${policy} /etc/apparmor.d/

apparmor_parser -r -W  /etc/apparmor.d/$(basename $policy)

echo
echo Added policy $(basename $policy) to apparmor.
echo
echo To remove the policy:
echo apparmor_parser -R /etc/apparmor.d/$(basename $policy)
echo
