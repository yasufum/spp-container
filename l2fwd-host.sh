#!/bin/sh

COREMASK=0x0f
PORTMASK=0x03
MEM=1024

SOCK_ID1=0
SOCK_ID2=1

sudo rm -rf /tmp/sock${SOCK_ID1}
sudo rm -rf /tmp/sock${SOCK_ID2}

sudo $RTE_SDK/examples/l2fwd/build/app/l2fwd \
  -c ${COREMASK} -n 4 \
  --socket-mem ${MEM} \
  --proc-type auto \
  -b 2a:00.0 -b 2a:00.1 \
  --file-prefix l2fwd-host \
  --vdev eth_vhost${SOCK_ID1},iface=/tmp/sock${SOCK_ID1},queues=2 \
  --vdev eth_vhost${SOCK_ID2},iface=/tmp/sock${SOCK_ID2},queues=2 \
  -- \
  -p ${PORTMASK}
