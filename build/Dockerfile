FROM ubuntu:latest

ENV HOMEDIR "/root"
ENV RTE_SDK "${HOMEDIR}/dpdk"
ENV RTE_TARGET "x86_64-native-linuxapp-gcc"
ENV PATH "$RTE_SDK/$RTE_TARGET/app:$PATH"
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
    libpcap-dev \
    wget \
    tmux \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $HOMEDIR
RUN git clone http://dpdk.org/git/dpdk
RUN git clone http://dpdk.org/git/apps/pktgen-dpdk
RUN git clone http://dpdk.org/git/apps/spp

# Compile DPDK, pktgen and SPP
WORKDIR $RTE_SDK
RUN make install T=$RTE_TARGET
RUN make app T=$RTE_TARGET
RUN make examples T=$RTE_TARGET

WORKDIR $HOMEDIR/pktgen-dpdk
RUN make

WORKDIR $HOMEDIR/spp
RUN make


# Set working directory when container is launched
WORKDIR $HOMEDIR
ADD env.sh $HOMEDIR/env.sh
RUN echo "source ${HOMEDIR}/env.sh" >> $HOMEDIR/.bashrc
