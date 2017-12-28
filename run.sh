#!/bin/bash

TARGET=spp
CMD=bash
WORKDIR=/usr/src/dpdk

docker-compose run \
	-e http_proxy=$http_proxy \
	-e https_proxy=$https_proxy \
	-e HTTP_PROXY=$http_proxy \
	-e HTTPS_PROXY=$https_proxy \
	-e RTE_SDK=$WORKDIR/dpdk \
	-e RTE_TARGET=$RTE_TARGET \
	$TARGET $CMD
