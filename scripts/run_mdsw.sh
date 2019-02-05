#!/bin/bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This runs minidump-stackwalk just like it runs in the processor. This
# will help debug minidump-stackwalk problems.
#
# Usage:
#
#    app@socorro:/app$ ./scripts/run_mdsw.sh [CRASHID]

set -e

# First convert configman environment vars which have bad identifiers to ones
# that don't
function getenv {
    python -c "import os; print(os.environ['$1'])"
}

DATADIR=./crashdata_mdsw_tmp
STACKWALKER="$(getenv 'processor.command_pathname')"

if [[ $# -eq 0 ]]; then
    echo "Usage: run_mdsw.sh CRASHID"
    exit 1
fi

mkdir "${DATADIR}" || echo "${DATADIR} already exists."

# Pull down the data for the crash if we don't have it, yet
if [ ! -f "${DATADIR}/v1/dump/$1" ]; then
    echo "Fetching crash data..."
    ./socorro-cmd fetch_crash_data "${DATADIR}" $1
fi

# Find the raw crash file
RAWCRASHFILE=$(find ${DATADIR}/v2/raw_crash/ -name $1 -type f)

timeout -s KILL 600 "${STACKWALKER}" \
    --raw-json $RAWCRASHFILE \
    --symbols-url "https://s3-us-west-2.amazonaws.com/org.mozilla.crash-stats.symbols-public/v1" \
    --symbols-cache /tmp/symbols/cache \
    --symbols-tmp /tmp/symbols/tmp \
    ${DATADIR}/v1/dump/$1