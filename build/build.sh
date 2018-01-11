#!/bin/sh

TARGET=spp-container
DIR=`dirname ${0}`

cp ${DIR}/../env.sh ${DIR}/

if [ ! -e env.sh ]; then
  echo "Error: env.sh doesn't exist!"
  exit
else
  sudo docker build \
	  --build-arg http_proxy=$http_proxy \
	  --build-arg https_proxy=$https_proxy \
	  -t $TARGET $DIR
  rm ${DIR}/env.sh
fi
