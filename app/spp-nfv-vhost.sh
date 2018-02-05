#!/bin/sh

SEC_ID=$1
CORELIST=$2
DEV_ID=$4

MEM=1024
CTRL_IP=$3
CTRL_PORT=6666

CONTAINER_NAME=spp-container

APP_DIR=`dirname ${0}`

# Include env.sh
. ${APP_DIR}/../env.sh

# vhost device
sock_host=/tmp/sock${DEV_ID}
sock_guest=/var/run/usvhost${DEV_ID}

CMD=${RTE_SDK}/../spp/src/nfv/${RTE_TARGET}/spp_nfv

cd ${APP_DIR}; \
  sudo docker run -i -t \
  --privileged \
  -v ${sock_host}:${sock_guest} \
  -v /dev/hugepages:/dev/hugepages \
  -v /var/run/:/var/run/ \
  ${CONTAINER_NAME} \
  ${CMD} \
  -l ${CORELIST} -n 4 -m ${MEM} \
  --vdev=virtio_user${DEV_ID},path=${sock_guest} \
  --proc-type=secondary \
  -- \
  -n ${SEC_ID} \
  -s ${CTRL_IP}:${CTRL_PORT}
