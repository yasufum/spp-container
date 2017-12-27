#!/bin/bash

SPP_DIR=$HOME/dpdk-home/spp
TARGET=golang
CMD=bash

docker-compose run \
	-e http_proxy=$http_proxy \
	-e https_proxy=$https_proxy \
	-e HTTP_PROXY=$http_proxy \
	-e HTTPS_PROXY=$https_proxy \
	$TARGET $CMD
