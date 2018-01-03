FROM ubuntu:latest

ENV WORKDIR "/usr/src/dpdk"
ENV RTE_SDK "$WORKDIR/dpdk"
ENV RTE_TARGET "x86_64-native-linuxapp-gcc"
ENV PATH "$PATH:$RTE_SDK/$RTE_TARGET/app"
ENV http_proxy "$http_proxy"
ENV https_proxy "$https_proxy"
ENV no_proxy "$no_proxy"

RUN apt-get update && apt-get install -y \
    vim \
    git \
    gcc \
    python \
    pciutils \
    make \
    libnuma-dev \
    gcc-multilib \
    libarchive-dev \
    linux-headers-$(uname -r) \
    tmux \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $WORKDIR
RUN git clone http://dpdk.org/git/dpdk
RUN git clone http://dpdk.org/git/apps/spp

# Compile jDPDK and SPP
WORKDIR $WORKDIR/dpdk
RUN make install T=$RTE_TARGET
WORKDIR $WORKDIR/dpdk/examples/l2fwd
RUN make

WORKDIR $WORKDIR/spp
RUN make

# Set working directory when container is launched
WORKDIR $WORKDIR
