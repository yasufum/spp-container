#!/bin/sh

CORE_LIST=0-1
PORT_MASK=0x03
NOF_RING=8

MEM=1024
CTRL_PORT=5555

CONTAINER_NAME=spp-container

if [ ! -z $1 ];then
  CTRL_IP=$1
elif [ ! -z ${SPP_CTRL_IP} ];then
  CTRL_IP=${SPP_CTRL_IP}
else
  echo "Invalid argument"
  exit
fi

APP_DIR=`dirname ${0}`

# Include env.sh
. ${APP_DIR}/../env.sh

CMD=${RTE_SDK}/../spp/src/primary/${RTE_TARGET}/spp_primary

cd ${APP_DIR}; \
  sudo docker run -i -t \
  --privileged \
  -v /dev/hugepages:/dev/hugepages \
  -v /var/run/:/var/run/ \
  ${CONTAINER_NAME} \
  ${CMD} \
  -l ${CORE_LIST} -n 4 -m ${MEM} \
  --huge-dir=/dev/hugepages \
  --proc-type=primary \
  -- \
  -p ${PORT_MASK} \
  -n ${NOF_RING} \
  -s ${CTRL_IP}:${CTRL_PORT}
