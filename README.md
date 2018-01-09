# SPP Container

Running SPP and DPDK applications on containers.


## Overview

This is a tools for running SPP and DPDK applications with docker.
It consists of shell scripts for building images and launching
containers with docker commands.

First of all, you need to build an image in which DPDK and other tools
are installed.
Just run `build/build.sh` to launch `docker build` with environment
variables.

```sh
$ build/build.sh
```

Waiting for minutes and you are ready to launch containers.

SPP is launched on host as described in SPP
[setup guide](http://dpdk.org/browse/apps/spp/tree/docs/setup_guide.md).

After SPP is launched, you run `app/spp-nfv.sh` for secondary which has
ring interface. It takes three arguments, secondary ID, core list and IP
address of the host.
It depends on your environment.
Notice that you cannot use `127.0.0.1' or `localhost` because this IP
address is used from inside container to access the host.

```sh
$ app/spp-nfv.sh 2 4-5 192.168.1.1
```

You also use vhost interface. For this case, you need to launch a
secondary on host to create socket.
If you create `/tmp/sock0` from SPP controller typing
`sec 1; add vhost 0`, container is launched as following.
In addition to previous example, it requires fourth argument
for specifying vhost ID.

```sh
$ app/spp-vm.sh 2 4-5 192.168.1.1 0
```

You can use secondaries running on containers as same as running
host or VMs.


## Install

* docker
* DPDK 17.11 or later (supporting container)
* pktgen-dpdk 3.4.6 or later
  (possible to run previous versions supporting DPDK 17.11)

### Optional

It is under consideration to launch serveral containers with
docker-compose. Some of scripts use docker-compose instead of
`docker run`.

* docker-compose


## How to use

This project supports not only SPP but also testpmd and pktgen-dpdk.
It consists of shell scripts and configuration files and categorized
in three types of tools considering phases.
Build tool is for creating container image.
Second one is for launching applications on host.
Final one is application launchers running inside containers.

```sh
$ tree spp-container/
spp-container/
├── README.md
├── app
│   ├── docker-compose.yml
│   ├── l2fwd.sh
│   ├── pktgen-compose.sh
│   ├── pktgen.sh
│   ├── run.sh
│   ├── spp-nfv-vhost.sh
│   ├── spp-nfv.sh
│   ├── spp-vm.sh
│   └── testpmd.sh
├── build
│   ├── Dockerfile
│   └── build.sh
├── env.sh
├── l2fwd-host.sh
├── pktgen-host.sh
└── testpmd-host.sh
```

### 1. Build tool

As explained in `Overview` section, build is done by simply typing
`build/build.sh`. It defines a name of image and runs `docker build`
with this name and some environments for applying inside container.
Environmental variables for container is defined in `env.sh`.

```sh
# env.sh
export RTE_SDK=/root/dpdk
export RTE_TARGET=x86_64-native-linuxapp-gcc
```

### 2. Host application launcher

It is mainly for testing behaviour of DPDK's container support and
you do not need to use it if you just only use SPP.
There are three scripts for applications with vhost interface for
communicating with containers.

  * l2fwd-host.sh
  * pktgen-host.sh
  * testpmd-host.sh

It is configured to provide two vhost interfaces and portmask is
`0x03`(means four ports) in default.
Physical ports are excluded with `-b` option (blacklist) of DPDK.

Please edit it for chaning configuration to adjust to your environment.


### 3. Application container launcher

All of application launchers are placed in `app/`.

As described by name, for instance, `pktgen.sh` launches pktgen-dpdk
inside a container and `pktgen-compose.sh` does it by using
`docker-compose`.

```sh
app
├── docker-compose.yml
├── l2fwd.sh
├── pktgen-compose.sh
├── pktgen.sh
├── run.sh
├── spp-nfv-vhost.sh
├── spp-nfv.sh
├── spp-vm.sh
└── testpmd.sh
```

If you use SPP, launch SPP before and run `spp-nfv.sh` for ring
interface or `spp-vm.sh` for vhost interface.
You cannot use `spp-nfv-vhost.sh` because it is expected to use
vdev but DPDK does not support vdev to be shared with secondary
processes currently.
It should be supported in a future release of DPDK.

You also use application launchers without SPP for testing.
In this case, you need to launch application on host before running
application launchers as described in previous section.
You can run any combination of applications other than SPP.
For instance, it is possible to run pktgen-dpdk on host and
testpmd on an container.

There is a restriction for using virtio_user with `--vdev` option.
DPDK might not support to use two or more virtio_user interfaces.
So, you are succeeded to launch application but forwarding does not
work properly. `app/l2fwd.sh` mignt not work for the reason.

`app/run.sh` launches a container without vhost interface and run any
of commands for inspecting status of the container or confirm how to
work. It is just used for debugging.


## How to run docker without sudo

Most of scripts provided in this project require to run docker with
sudo because for running DPDK.
However, you can run docker without sudo if you do not use DPDK.

In general, you need to run docker with sudo because docker daemon
binds to a unix socket instead of a TCP port.
Unix socket is owned by root and other users can only access it using
sudo.
However, you can run if you add your account to docker group.

```sh
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

To activate it, logout and re-login at once.
