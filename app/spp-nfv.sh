#!/bin/sh

SEC_ID=$1
CORELIST=$2

MEM=1024
CTRL_PORT=6666

CONTAINER_NAME=spp-container

if [ ! -z $3 ];then
  CTRL_IP=$3
elif [ ! -z ${SPP_CTRL_IP} ];then
  CTRL_IP=${SPP_CTRL_IP}
else
  echo "Invalid argument"
  exit
fi

APP_DIR=`dirname ${0}`

# Include env.sh
. ${APP_DIR}/../env.sh

CMD=${RTE_SDK}/../spp/src/nfv/${RTE_TARGET}/spp_nfv

cd ${APP_DIR}; \
  sudo docker run -i -t \
  --privileged \
  -v /dev/hugepages:/dev/hugepages \
  -v /var/run/:/var/run/ \
  -v /tmp/:/tmp/ \
  ${CONTAINER_NAME} \
  ${CMD} \
  -l ${CORELIST} -n 4 -m ${MEM} \
  --proc-type=secondary \
  -- \
  -n ${SEC_ID} \
  -s ${CTRL_IP}:${CTRL_PORT}
