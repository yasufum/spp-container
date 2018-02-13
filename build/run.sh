#!/bin/bash

CMD=$1
APP_DIR=`dirname ${0}`
CONTAINER_NAME=spp-container
ENVSH=${APP_DIR}/env.sh

# Include env.sh
if [ -e ${ENVSH} ];then
  . ${ENVSH}
else
  _build_env='./build/build.py --only-envsh'
  echo "[Error] ${ENVSH} does not exist!"
  echo "You have to build image or run '${_build_env}' to create it."
  exit
fi

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
