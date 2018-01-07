#!/bin/sh

APP_DIR=`dirname ${0}`

CORELIST=7-9
MEM=2048

TARGET=pktgen1

DEV_ID=1

# vhost device
sock_guest=/var/run/usvhost${DEV_ID}

# Include env.sh
. ${APP_DIR}/../env.sh

CMD=${RTE_SDK}/../pktgen-dpdk/app/${RTE_TARGET}/pktgen

cd ${APP_DIR}; \
  sudo docker-compose run \
	-e http_proxy=${http_proxy} \
	-e https_proxy=${https_proxy} \
	-e HTTP_PROXY=${http_proxy} \
	-e HTTPS_PROXY=${https_proxy} \
	-e RTE_SDK=${RTE_SDK} \
	-e RTE_TARGET=${RTE_TARGET} \
  ${TARGET} ${CMD} \
  -l ${CORELIST} \
  -n 4 \
  -m ${MEM}\
  --vdev=virtio_user${DEV_ID},path=${sock_guest} \
  --file-prefix=container-pktgen2 \
  --proc-type auto --log-level 7 \
  -- \
  -T -P \
  -m [8:9].0 \
  -f themes/white-black.theme
