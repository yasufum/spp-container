#!/bin/sh

SEC_ID=$1
CORELIST=$2
DEV_ID=0

MEM=1024
CTRL_IP=$3
CTRL_PORT=6666

CONTAINER_NAME=spp-container

APP_DIR=`dirname ${0}`

# Include env.sh
. ${APP_DIR}/../env.sh

# vhost device
sock_host1=/tmp/sock${DEV_ID}
sock_guest1=/var/run/usvhost${DEV_ID}

CMD=${RTE_SDK}/../spp/src/nfv/${RTE_TARGET}/spp_nfv

cd ${APP_DIR}; \
  sudo docker run -i -t \
  -v ${sock_host1}:${sock_guest1} \
  -v /dev/hugepages:/dev/hugepages \
  -v /var/run/:/var/run/ \
  ${CONTAINER_NAME} \
  ${CMD} \
  -l ${CORELIST} -n 4 -m ${MEM} \
  --vdev=virtio_user${DEV_ID},path=${sock_guest1} \
  --proc-type=secondary \
  -- \
  -n ${SEC_ID} \
  -s ${CTRL_IP}:${CTRL_PORT}
