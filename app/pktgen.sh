#!/bin/sh

APP_DIR=`dirname ${0}`
CONTAINER_NAME=spp-container

DEV_ID1=0
CORELIST=4-6
MEM=2048

# Include env.sh
. ${APP_DIR}/../env.sh

CMD=${RTE_SDK}/../pktgen-dpdk/app/${RTE_TARGET}/pktgen

# vhost device
sock_host=/tmp/sock${DEV_ID1}
sock_guest=/var/run/usvhost${DEV_ID1}

cd ${APP_DIR}; \
  sudo docker run -i -t \
  --workdir ${RTE_SDK}/../pktgen-dpdk \
  -v ${sock_host}:${sock_guest} \
  -v /dev/hugepages:/dev/hugepages \
  ${CONTAINER_NAME} \
  ${CMD} \
  -l ${CORELIST} \
  -n 4 \
  -m ${MEM}\
  --vdev=virtio_user${DEV_ID1},path=${sock_guest} \
  --file-prefix=container-pktgen0 \
  --proc-type auto --log-level 7 \
  -- \
  -T -P \
  -m [5:6].0 \
  -f themes/white-black.theme
