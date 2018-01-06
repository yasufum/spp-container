#!/bin/sh

COREMASK=0x0f
PORTMASK=0x0f
MEM=1024

SOCK_ID1=0
SOCK_ID2=1

sudo rm -rf /tmp/sock${SOCK_ID1}
sudo rm -rf /tmp/sock${SOCK_ID2}

sudo $RTE_SDK/examples/l2fwd/build/app/l2fwd \
  -c ${COREMASK} -n 4 \
  --socket-mem ${MEM} \
  --proc-type auto \
  --file-prefix l2fwd-host \
  --vdev eth_vhost${SOCK_ID1},iface=/tmp/sock${SOCK_ID1},queues=2 \
  --vdev eth_vhost${SOCK_ID2},iface=/tmp/sock${SOCK_ID2},queues=2 \
  -- \
  -p ${PORTMASK}
