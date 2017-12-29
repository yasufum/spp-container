#!/bin/bash

TARGET=spp
CMD=$1
#WORKDIR=/usr/src/dpdk

if [ ! $1 ]; then
  echo "usage: $0 [command]"
  exit
fi

sudo docker-compose run \
	-e http_proxy=${http_proxy} \
	-e https_proxy=${https_proxy} \
	-e HTTP_PROXY=${http_proxy} \
	-e HTTPS_PROXY=${https_proxy} \
	-e RTE_SDK=${WORKDIR}/dpdk \
	-e RTE_TARGET=${RTE_TARGET} \
	${TARGET} ${CMD}
