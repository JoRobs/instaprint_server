#!/usr/bin/env bash

# requires sudo and apparmor-utils
#
# > sudo apt install apparmor-utils
#

set -euo pipefail

script_dir=$(dirname $0)

# Use docker built in security options to load custom template
# add custom apparmor policy
apparmor_parser -r -W ${script_dir}/docker-allow-dbus.apparmor.policy

# To remove the policy
#apparmor_parser -R /path/to/profile