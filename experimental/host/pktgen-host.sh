#!/bin/sh

CORELIST=0-4
MEM=2048
SOCK_ID0=0
SOCK_ID1=1

sudo rm -rf /tmp/sock${SOCK_ID0}
sudo rm -rf /tmp/sock${SOCK_ID1}

CMD=app/${RTE_TARGET}/pktgen

cd ../pktgen-dpdk;sudo ${CMD} \
  -l ${CORELIST} \
  -n 4 \
  -m ${MEM}\
  --file-prefix pktgen-host \
  --vdev eth_vhost${SOCK_ID0},iface=/tmp/sock${SOCK_ID0},queues=2 \
  --vdev eth_vhost${SOCK_ID1},iface=/tmp/sock${SOCK_ID1},queues=2 \
  --proc-type auto --log-level 7 \
  -b 2a:00.0 -b 2a:00.1 \
  -- \
  -T -P \
  -m [1:2].0 -m [3:4].1 \
  -f themes/white-black.theme
