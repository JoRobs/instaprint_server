#!/usr/bin/env bash

# Adds a docker-default policy to apparmor.d then disables
# it to allow docker to do some things it normally can't.
# requires sudo and apparmor-utils
#
# > sudo apt install apparmor-utils
#

set -euo pipefail

if [ -e /etc/apparmor.d/docker-default ]; then
  cp /etc/apparmor.d/docker-default /etc/apparmor.d/docker-default.$(date +%s).backup
fi

cp docker-default.apparmor.policy /etc/apparmor.d/docker-default

aa-disable docker-default
