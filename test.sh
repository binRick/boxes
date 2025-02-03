#!/usr/bin/env bash
set -eou pipefail
source .v/bin/activate

#THICKNESS=3.0
THICKNESS=6.0
D1=10.0

find boxes/generators -name "*.py"|xargs -I % python3 -m py_compile %

[[ -d build ]] && mv build .b && rm -rf .b &
pip install .||true
[[ -f t1.svg ]] && unlink t1.svg
./scripts/boxes ABoxx \
	--format svg \
	--thickness $THICKNESS \
	--d1 $D1 \
	--output t1.svg
open -g t1.svg
