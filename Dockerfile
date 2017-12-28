FROM ubuntu:latest

WORKDIR /usr/src/dpdk
#ADD ../spp /usr/src/dpdk

ENV PATH "$PATH:/usr/src/dpdk/x86_64-native-linuxapp-gcc/app/"
ENV http_proxy "$http_proxy"
ENV https_proxy "$https_proxy"
ENV no_proxy "$no_proxy"
ENV RTE_SDK "$WORKDIR/dpdk"
ENV RTE_TARGET "x86_64-native-linuxapp-gcc"

RUN apt-get update && apt-get install -y \
    vim \
    git \
    gcc \
    make \
    libnuma-dev \
    gcc-multilib \
    libarchive-dev \
    linux-headers-$(uname -r) \
    tmux \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN git clone http://dpdk.org/git/dpdk
RUN git clone http://dpdk.org/git/apps/spp
