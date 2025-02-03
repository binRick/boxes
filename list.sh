#!/usr/bin/env bash
set -eou pipefail
source .v/bin/activate
./scripts/boxes --list
