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

Build a docker image in which DPDK and SPP are installed instructed as a
Dockerfile.
For building image, just run `build/build.sh` using latest releases.
This shell script launchs `docker build`.
Waiting for a minutes and you are ready to launch containers.

```sh
$ build/build.sh
```

If you want to use specific branch of the release or repository, run `build.sh`
with options. Please refer help `build/build.py -h` for details.


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
Build tool is for creating container image,
application launchers are for running inside containers and
experimental tools.

```sh
$ tree spp-container/
spp-container/
├── README.md
├── app
│   ├── __init__.py
│   ├── common.py
│   ├── conf.py
│   ├── l2fwd.py
│   ├── pktgen-sec.py
│   ├── pktgen.py
│   ├── spp-nfv.py
│   ├── spp-primary.py
│   ├── spp-vm.py
│   └── testpmd.py
├── build
│   ├── Dockerfile
│   ├── run.sh
│   └── build.sh
├── compose
│   ├── docker-compose.yml
│   └── pktgen-compose.sh
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

If you want to use developing version of SPP 'https://github.com/your/spp.git'
with DPDK 17.11,
you can build an image of DPDK 17.11 and developping repository.

```sh
./build/build.py --dpdk-branch v17.11 --spp-repo https://github.com/your/spp.git
```

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

Container is useful for setting up NFVs, but just bit messy to lookup inside the
container because it is cleaned up immediately after process is finished.
To inspect inside the container, `build/run.sh` is useful.
It launches the container and run any of command without DPDK interfaces
for just inspecting the container.
`build/run.sh` uses `env.sh` created from `build/build.sh` to include
environment variables, so do not remove it.


### 2. Application container launcher

Application container launchers are placed in `app/`.

```sh
app
├── __init__.py
├── common.py
├── conf.py
├── l2fwd.py
├── pktgen-sec.py
├── pktgen.py
├── spp-nfv.py
├── spp-primary.py
├── spp-vm.py
└── testpmd.py
```

As described by name, for instance, `pktgen.py` launches pktgen-dpdk
inside a container.

For launching application containers with SPP, launch SPP controller and
then primary and secondary processes before.
However, you have to define 'SPP_CTRL_IP' environment variable
to indicate IP address of controller for SPP processes on containers before.

You need to open several terminals for running each of processes.


#### SPP Controller

SPP controller is a CLI tool for accepting user's commands.
You do not need a container specific controller.
Simply use `spp.py` provided in SPP project.

```sh
$ cd /path/to/spp
$ python spp.py
```


#### SPP Primary Container

SPP primary is launched from `app/spp-primary.py`. It runs on a container
and manages resources on host from inside the container.
Resources on host is able to be managed from application container
because `app/spp-primary.py` calls `docker run` with
`-v` option to mount hugepages or other devices and share them between
host and containers.

There are two usecases for running SPP primary.
Showing statistics of traffic information or not.

If you launch SPP primary with statistics, you need to run it with
two cores and in foreground mode.
This is an example for launching primary with core list 0-1 and two ports
in foreground mode.

```sh
$ ./app/spp-primary -l 0-1 -p 0x03 -fg
```

It is another example with one core and two ports in background mode.

```sh
$ ./app/spp-primary -l 0 -p 0x03
```

You can use other options than explained. Please refer help.

```sh
$ ./app/spp-primary.py -h
usage: spp-primary.py [-h] [-n NOF_RING] [-p PORT_MASK] [-l CORE_LIST]
                      [-c CORE_MASK] [-m MEM] [--socket-mem SOCKET_MEM]
                      [-ip CTRL_IP] [--ctrl-port CTRL_PORT]
                      [--nof-memchan NOF_MEMCHAN]
                      [--container-name CONTAINER_NAME] [-fg]

Launcher for spp-nfv applicatino container

optional arguments:
  -h, --help            show this help message and exit
  -n NOF_RING, --nof-ring NOF_RING
                        Maximum number of Ring PMD
  -p PORT_MASK, --port-mask PORT_MASK
                        Port mask
  -l CORE_LIST, --core-list CORE_LIST
                        Core list
  -c CORE_MASK, --core-mask CORE_MASK
                        Core mask
  -m MEM, --mem MEM     Memory size for spp_nfv
  --socket-mem SOCKET_MEM
                        Memory size for spp_nfv
  -ip CTRL_IP, --ctrl-ip CTRL_IP
                        IP address of SPP controller
  --ctrl-port CTRL_PORT
                        Port of SPP controller
  --nof-memchan NOF_MEMCHAN
                        Port of SPP controller
  --container-name CONTAINER_NAME
                        Name of container image
  -fg, --foreground     Run container as foreground mode
```


#### SPP Secondary Container

In SPP, there are two types of secondary process, `spp_nfv`
for forwarding packets on host,
or `spp_vm` for forwarding inside a VM.
`spp-nfv.py` is for launching application container for `spp_nfv`
with ring interfaces
or `spp-vm.py` for vhost interface.

`spp-nfv.py` requires a secondary ID and core option, core mask or
core list.

```sh
$ app/spp-nfv.py -i 1 -l 2-3
```

You can specify other options as DPDK applications.

```sh
$ ./app/spp-nfv.py -h
usage: spp-nfv.py [-h] [-i SEC_ID] [-l CORE_LIST] [-c CORE_MASK] [-m MEM]
                  [--socket-mem SOCKET_MEM] [-ip CTRL_IP]
                  [--ctrl-port CTRL_PORT] [--nof-memchan NOF_MEMCHAN]
                  [--container-name CONTAINER_NAME] [-fg]

Launcher for spp-nfv applicatino container

optional arguments:
  -h, --help            show this help message and exit
  -i SEC_ID, --sec-id SEC_ID
                        Secondary ID
  -l CORE_LIST, --core-list CORE_LIST
                        Core list
  -c CORE_MASK, --core-mask CORE_MASK
                        Core mask
  -m MEM, --mem MEM     Memory size for spp_nfv
  --socket-mem SOCKET_MEM
                        Memory size for spp_nfv
  -ip CTRL_IP, --ctrl-ip CTRL_IP
                        IP address of SPP controller
  --ctrl-port CTRL_PORT
                        Port of SPP controller
  --nof-memchan NOF_MEMCHAN
                        Port of SPP controller
  --container-name CONTAINER_NAME
                        Name of container image
  -fg, --foreground     Run container as foreground mode
```

For launching `spp_vm` for vhost interface, it is required to assign
a vhost device ID from `app/spp-nfv.py` and launch `app/spp-vm.py`
with same ID..

```sh
# Add vhost 1 from spp-nfv.py of sec 1
spp > sec 1;add vhost 1
```

Launch a secondary container with device ID 1.

```sh
$ app/spp-vm.py -i 2 -l 4-5 -d 1
```

You can specify other options as DPDK applications.

```sh
$ ./app/spp-vm.py -h
usage: spp-vm.py [-h] [-i SEC_ID] [-l CORE_LIST] [-c CORE_MASK] [-m MEM]
                 [--socket-mem SOCKET_MEM] [-d DEV_ID] [-ip CTRL_IP]
                 [--ctrl-port CTRL_PORT] [-n NOF_MEMCHAN]
                 [--container-name CONTAINER_NAME] [-fg]

Launcher for spp-nfv applicatino container

optional arguments:
  -h, --help            show this help message and exit
  -i SEC_ID, --sec-id SEC_ID
                        Secondary ID
  -l CORE_LIST, --core-list CORE_LIST
                        Core list
  -c CORE_MASK, --core-mask CORE_MASK
                        Core mask
  -m MEM, --mem MEM     Memory size for spp_nfv
  --socket-mem SOCKET_MEM
                        Memory size for spp_nfv
  -d DEV_ID, --dev-id DEV_ID
                        vhost device ID
  -ip CTRL_IP, --ctrl-ip CTRL_IP
                        IP address of SPP controller
  --ctrl-port CTRL_PORT
                        Port of SPP controller
  -n NOF_MEMCHAN, --nof-memchan NOF_MEMCHAN
                        Port of SPP controller
  --container-name CONTAINER_NAME
                        Name of container image
  -fg, --foreground     Run container as foreground mode
```

[TODO] Add other app containers


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
