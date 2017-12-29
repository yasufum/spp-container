#!/bin/sh

TARGET=spp-container
DIR=.

sudo docker build -t $TARGET $DIR
