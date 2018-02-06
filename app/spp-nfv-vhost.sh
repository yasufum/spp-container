#!/bin/sh

SEC_ID=$1
CORELIST=$2
DEV_ID=$3

MEM=1024
CTRL_PORT=6666

CONTAINER_NAME=spp-container

if [ ! -z $4 ];then
  CTRL_IP=$4
elif [ ! -z ${SPP_CTRL_IP} ];then
  CTRL_IP=${SPP_CTRL_IP}
else
  echo "Invalid argument"
  exit
fi

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
