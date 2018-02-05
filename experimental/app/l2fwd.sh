#!/bin/sh


APP_DIR=`dirname ${0}`
CONTAINER_NAME=spp-container

# Include env.sh
. ${APP_DIR}/../../env.sh

CMD=${RTE_SDK}/examples/l2fwd/${RTE_TARGET}/l2fwd

DEV_ID1=0
DEV_ID1=1
CORELIST=4-5
PORTMASK=0x03
MEM=1024

# vhost device
sock_host1=/tmp/sock${DEV_ID1}
sock_guest1=/var/run/usvhost${DEV_ID1}
sock_host2=/tmp/sock${DEV_ID2}
sock_guest2=/var/run/usvhost${DEV_ID2}

cd ${APP_DIR}; \
  sudo docker run -i -t \
  -v ${sock_host1}:${sock_guest1} \
  -v ${sock_host2}:${sock_guest2} \
  -v /dev/hugepages:/dev/hugepages \
  ${CONTAINER_NAME} \
  ${CMD} -l ${CORELIST} \
  -n 4 \
  -m ${MEM}\
  --vdev=virtio_user${DEV_ID1},path=${sock_guest1} \
  --vdev=virtio_user${DEV_ID2},path=${sock_guest2} \
  --file-prefix=container \
  -- \
  -p ${PORTMASK}
