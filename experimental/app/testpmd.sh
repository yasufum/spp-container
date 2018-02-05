#!/bin/sh

CORELIST=$2
MEM=1024

CONTAINER_NAME=spp-container
DEV_ID=$1

APP_DIR=`dirname ${0}`

# vhost device
sock_host1=/tmp/sock${DEV_ID}
sock_guest1=/var/run/usvhost${DEV_ID}

cd ${APP_DIR}; \
  sudo docker run -i -t \
  -v ${sock_host1}:${sock_guest1} \
  -v /dev/hugepages:/dev/hugepages \
  ${CONTAINER_NAME} \
  testpmd -l ${CORELIST} -n 4 -m ${MEM} \
  --no-pci \
  --vdev=virtio_user${DEV_ID},path=${sock_guest1} \
  --file-prefix=container${DEV_ID} \
  -- -i \
  --txqflags=0xf00 --disable-hw-vlan
