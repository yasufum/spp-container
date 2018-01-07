#!/bin/bash

CMD=$1
APP_DIR=`dirname ${0}`
CONTAINER_NAME=spp-container

# Include env.sh
. ${APP_DIR}/../env.sh

if [ ! $1 ]; then
  echo "usage: $0 [command]"
  exit
fi

cd ${APP_DIR}; \
  sudo docker run -i -t \
	-e http_proxy=${http_proxy} \
	-e https_proxy=${https_proxy} \
	-e HTTP_PROXY=${http_proxy} \
	-e HTTPS_PROXY=${https_proxy} \
	-e RTE_SDK=${RTE_SDK} \
	-e RTE_TARGET=${RTE_TARGET} \
	${CONTAINER_NAME} \
  ${CMD}
