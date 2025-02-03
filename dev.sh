#!/usr/bin/env bash
set -eou pipefail

nodemon -w . ${@:-} \
	-i build -i .v -i boxes/generators/__pycache__ \
	-e py,sh \
		-x ./test.sh
