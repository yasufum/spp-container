# SPP Container

Running SPP and DPDK applications on containers.


## Overview

SPP container is a set of tools for running SPP and DPDK applications
with docker.
It consists of shell or python scripts for building images and launching
containers with docker commands.

## Getting Started

### Setup for DPDK

First of all, you need to setup hugepages for running DPDK application
as described in DPDK's
[Gettting Started Guide](https://dpdk.org/doc/guides/linux_gsg/sys_reqs.html).
You also need to load kernel modules and bind network ports as in
[Linux Drivers](https://dpdk.org/doc/guides/linux_gsg/linux_drivers.html).

### Build Docker Image

Build a docker image in which DPDK and SPP are installed with
Dockerfile. For building image, just run `build/build.sh` to launch
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
It is better to this variable in `$HOME/.bashrc`.

```sh
# Set host IP address
export SPP_CTRL_IP=192.168.1.11
```

For primary process on a container, run 'spp-primary.py' with options
EAL and SPP primary.

```sh
# Terminal 2
$ ./app/spp-primary.py -l 0-1 -p 0x03
```

For secondary process, there are two launcher scripts.
`spp-nfv.py` is used for launching secondary process with ring PMD.
On the other hand, `spp-vm.py` is for vhost PMD.
There are similar to `spp_nfv` running on host and `spp_vm` running on
guest VM, but different both type of secondary processes are running
also on containers as primary.

Launch `spp_nfv` from `spp-nfv.py` with options.
In this case, secondary ID is `1` and core list is `2-3` for using
3rd and 4th cores.

```sh
# Terminal 3
$ app/spp-nfv.py -i 1 -l 2-3
```

Then, launch container with vhost PMD. However, you have to create a
socket from controller's terminal before.

```sh
# Terminal 1
spp > sec 1;add vhost 1
```

`sec 1` is the secondary process running on `terminal 3`.
Vhost ID is an arbitrary number, defined as `1` in this case.

Secondary process of vhost interface container is launched from
`spp-vm.py`. The name `vm` is originaly from `spp_vm` but process
runs on a container actually.

Options are almost same as `spp-nfv.py`, but additional option
for specifying vhost device ID is required with `-d`.
Value of `-d` must be the same as vhost ID.

```sh
# Terminal 4
$ app/spp-vm.py -i 2 -l 4-5 -d 1
```

## Install

* docker
* DPDK 17.11 or later (supporting container)
* SPP 17.11 or later

### Optional

It is under consideration to launch serveral containers with
docker-compose. Some of scripts use docker-compose instead of
`docker run`.

[TODO] Add implementation and explanation for docker-compose.

* docker-compose


## How to use

This project supports not only SPP but also other applications
containers such as testpmd or pktgen-dpdk.
It consists of python, shell scripts and configuration files.
Files are categorized in three types of tools considering phases,
build tool for creating container image,
application launchers running inside containers and
experimental tools.

```sh
$ tree spp-container/
spp-container/
├── README.md
├── app
│   ├── spp-primary.py
│   ├── spp-nfv.py
│   ├── spp-vm.py
│   ├── l2fwd.py
│   ├── pktgen.py
│   └── testpmd.py
├── build
│   ├── Dockerfile
│   ├── run.sh
│   └── build.sh
├── env.sh
└── experimental
    └── host
        ├── l2fwd-host.sh
        ├── pktgen-host.sh
        └── testpmd-host.sh
```

### 1. Build tool

As explained in `Overview` section, build process is done by simply
typing `build/build.py`.
This script is for running `docker build` with a set of `--build-args`
options for applying inside container.

Refer all of options running with `-h` option.

```sh
$ ./build/build.py -h
usage: build.py [-h] [-n CONTAINER_NAME] [--dpdk-repo DPDK_REPO]
                [--dpdk-branch DPDK_BRANCH] [--pktgen-repo PKTGEN_REPO]
                [--pktgen-branch PKTGEN_BRANCH] [--spp-repo SPP_REPO]
                [--spp-branch SPP_BRANCH]

Docker image builder for SPP

optional arguments:
  -h, --help            show this help message and exit
  -n CONTAINER_NAME, --container-name CONTAINER_NAME
                        Container name
  --dpdk-repo DPDK_REPO
                        Git url of DPDK
  --dpdk-branch DPDK_BRANCH
                        Specific branch for cloning DPDK
  --pktgen-repo PKTGEN_REPO
                        Git url of pktgen-dpdk
  --pktgen-branch PKTGEN_BRANCH
                        Specific branch for cloning pktgen-dpdk
  --spp-repo SPP_REPO   Git url of SPP
  --spp-branch SPP_BRANCH
                        Specific branch for cloning SPP
```

For testing purpose, `build/run.sh` launches a container without vhost
interface and run any of commands for inspecting status
of the container or confirm how to
work. `run.sh` uses `env.sh` created from `build.sh` to include
environment variables, so do not remove it..

### 2. Application container launcher

All of application launchers are placed in `app/`.

As described by name, for instance, `pktgen.py` launches pktgen-dpdk
inside a container.

```sh
app
├── spp-primary.py
├── spp-nfv.py
├── spp-vm.py
├── l2fwd.py
├── pktgen.py
└── testpmd.py
```

For using SPP, launch SPP before and run `spp-nfv.py` for ring
interface or `spp-vm.py` for vhost interface.
You cannot use `spp-nfv-vhost.py` because it is expected to use
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
work properly. `app/l2fwd.py` mignt not work for the reason.

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



## How to run docker without sudo

You are required to sudo for running docker in most of scripts provided
in this project.
It is because for running DPDK applications.

However, you can run docker without sudo if you do not use DPDK.
It is useful if you run `docker rm` or `docker rmi` commands.

```sh
# Remove all of containers
$ docker rm `docker ps -aq`

# Remove all of images
$ docker rmi `docker images -aq`
```

The reason for running docker requires sudo is docker daemon
binds to a unix socket instead of a TCP port.
Unix socket is owned by root and other users can only access it using
sudo.
However, you can run if you add your account to docker group.

```sh
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

To activate it, you have to logout and re-login at once.
