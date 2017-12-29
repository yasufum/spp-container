#!/bin/sh

CONTAINER_NAME=spp-container
DEV_ID1=1
DEV_ID1=2

# vhost device
sock_host1=/tmp/sock${DEV_ID1}
sock_guest1=/var/run/usvhost${DEV_ID1}
sock_host2=/tmp/sock${DEV_ID2}
sock_guest2=/var/run/usvhost${DEV_ID2}

sudo docker run -i -t \
  -v ${sock_host1}:${sock_guest1} \
  -v ${sock_host2}:${sock_guest2} \
  -v /dev/hugepages:/dev/hugepages \
  ${CONTAINER_NAME} \
  testpmd -l 4-5 -n 4 -m 1024 --no-pci \
  --vdev=virtio_user1,path=${sock_guest1} \
  --vdev=virtio_user2,path=${sock_guest2} \
  --file-prefix=container \
  -- -i --txqflags=0xf00 --disable-hw-vlan
