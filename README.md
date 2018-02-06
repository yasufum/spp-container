# SPP Container

Running SPP and DPDK applications on containers.


## Overview

SPP container is a set of tools for running SPP and DPDK applications
with docker.
It consists of shell or python scripts for building images and launching
containers with docker commands.

## Getting Started

### Setup for DPDK as in

First of all, you need to setup hugepages for running DPDK application
as described in DPDK's
[Gettting Started Guide](https://dpdk.org/doc/guides/linux_gsg/sys_reqs.html).
You also need to load kernel modules and bind network ports as in
[Linux Drivers](https://dpdk.org/doc/guides/linux_gsg/linux_drivers.html).

### Build Docker Image

Build a docker image in which DPDK is installed with Dockerfile.
For building image, just run `build/build.sh` to launch
`docker build` with environment variables.

```sh
$ build/build.sh
```

Waiting for a minutes and you are ready to launch containers.

### Launch SPP

In this section, you use four terminals for each of SPP processes.
First, get SPP and launch SPP controller.

```sh
# Terminal 1
$ git clone http://dpdk.org/git/apps/spp
$ cd spp/src
```

It runs as interactive mode for waiting user input.
So, you need to open other terminals for SPP primary and secondary
processes.

Before launch containers, set host IP address as 'SPP_CTRL_IP'
environment variable for processes inside containers enable to access
host.

```sh
# Set host IP address
export SPP_CTRL_IP=192.168.1.11
```

For primary process, run 'spp-primary.sh'. It uses core list
`0-1` which means 1st and 2nd cores as default.

```sh
# Terminal 2
$ ./app/spp-primary.sh
```

For secondary process, there are two launcher scripts.
`spp-nfv.sh` is used for launching secondary process with ring PMD.
On the other hand, `spp-vm.sh` is for vhost PMD.
There are similar to `spp_nfv` running on host and `spp_vm` running on
guest VM, but different both type of secondary processes are running on
containers.

Launch `spp_nfv` from `spp-nfv.sh` with options, secondary ID
and core list.
In this case, core list is `2-3` for using 3rd and 4th cores.

```sh
# Terminal 3
$ app/spp-nfv.sh 1 2-3
```

Then, launch container with vhost PMD. However, you need to create a
socket from controller terminal.

```sh
# Terminal 1
spp > sec 1;add vhost 1
```

`sec 1` is a secondary running in `terminal 3`.
The ID of vhost 1, in this case, is an arbitrary number.

```sh
# Terminal 4
$ app/spp-vm.sh 2 4-5 1
```

## Install

* docker
* DPDK 17.11 or later (supporting container)
* SPP 17.11 or later

### Optional

It is under consideration to launch serveral containers with
docker-compose. Some of scripts use docker-compose instead of
`docker run`.

* docker-compose


## How to use

This project supports not only SPP but also other applications
containers such as testpmd or pktgen-dpdk.
It consists of python, shell scripts and configuration files,
and categorized
in three types of tools considering phases.
First one is build tool for creating container image.
Second one is application launchers running inside containers.
Final one is experimental tools.

```sh
$ tree spp-container/
spp-container/
├── README.md
├── app
│   ├── spp-primary.sh
│   ├── spp-nfv.sh
│   ├── spp-vm.sh
│   ├── run.sh
│   ├── l2fwd.sh
│   ├── pktgen.sh
│   └── testpmd.sh
├── build
│   ├── Dockerfile
│   └── build.sh
├── env.sh
└── experimental
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

### 2. Application container launcher

All of application launchers are placed in `app/`.

As described by name, for instance, `pktgen.sh` launches pktgen-dpdk
inside a container and `pktgen-compose.sh` does it by using
`docker-compose`.

```sh
app
├── spp-primary.sh
├── spp-nfv.sh
├── spp-vm.sh
├── run.sh
├── l2fwd.sh
├── pktgen.sh
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

### 3. Experimental tools

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



## (Optional) How to run docker without sudo

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
