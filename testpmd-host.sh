#!/bin/sh

SOCK_ID1=1
SOCK_ID2=2

COREMASK=0x0f
MEM=1024

sudo rm -rf /tmp/sock${SOCK_ID1}
sudo rm -rf /tmp/sock${SOCK_ID2}

sudo $RTE_SDK/app/test-pmd/testpmd \
  -c ${COREMASK} -n 4 \
  --socket-mem ${MEM} \
  --proc-type auto \
  --file-prefix testpmd-host \
  --vdev eth_vhost${SOCK_ID1},iface=/tmp/sock${SOCK_ID1},queues=2 \
  --vdev eth_vhost${SOCK_ID2},iface=/tmp/sock${SOCK_ID2},queues=2 \
  -- \
  -i
