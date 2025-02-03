#!/usr/bin/env bash
set -eou pipefail
source .v/bin/activate

#THICKNESS=3.0
THICKNESS=6.0
D1=10.0

find boxes/generators -name "*.py"|xargs -I % python3 -m py_compile %

[[ -d build ]] && mv build .b && rm -rf .b &
pip install . &>/dev/null||true
[[ -f t1.svg ]] && unlink t1.svg
cmd="./scripts/boxes ABoxx \
	--format svg \
	--thickness $THICKNESS \
	--d1 $D1 \
	--output t1.svg"

if ! eval "$cmd" | grep -q "OK2025"; then
	echo -e "\n\nFailed to run boxes cmd \"$cmd\". Wanted OK2025 in output to validate.\n"
	exit 1
fi
if [[ ! -f t1.svg ]]; then
	echo -e "\n\nFailed to generate t1.svg!\n"
	exit 1
fi

echo -e "BUILD OK"

open -g t1.svg
