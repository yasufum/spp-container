#!/bin/sh

sudo rm /tmp/sock1
sudo rm /tmp/sock2

sudo $RTE_SDK/examples/l2fwd/build/app/l2fwd \
  -c 0x03 -n 4 \
  --socket-mem 1024 \
  --proc-type auto \
  --file-prefix l2fwd-host \
  --vdev eth_vhost1,iface=/tmp/sock1,queues=2 \
  --vdev eth_vhost2,iface=/tmp/sock2,queues=2 \
  -- \
  -p 0x03
