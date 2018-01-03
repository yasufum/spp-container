#!/bin/sh

sudo rm -rf /tmp/sock1
sudo rm -rf /tmp/sock2

sudo $RTE_SDK/app/test-pmd/testpmd \
  -c 0x0f -n 4 \
  --socket-mem 1024 \
  --proc-type auto \
  --file-prefix testpmd-host \
  --vdev eth_vhost1,iface=/tmp/sock1,queues=2 \
  --vdev eth_vhost2,iface=/tmp/sock2,queues=2 \
  -- \
  -i
  #-- -p 0x03
