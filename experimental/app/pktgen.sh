#!/bin/sh

MEM=2048

APP_DIR=`dirname ${0}`
CONTAINER_NAME=spp-container

DEV_ID=$1
CORELIST=$2

# Include env.sh
. ${APP_DIR}/../../env.sh

CMD=${RTE_SDK}/../pktgen-dpdk/app/${RTE_TARGET}/pktgen

# vhost device
sock_host=/tmp/sock${DEV_ID}
sock_guest=/var/run/usvhost${DEV_ID}

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
  --vdev=virtio_user${DEV_ID},path=${sock_guest} \
  --file-prefix=container-pktgen0 \
  --proc-type auto --log-level 7 \
  -- \
  -T -P \
  -m [5:6].0 \
  -f themes/white-black.theme
