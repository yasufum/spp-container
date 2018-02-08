#!/usr/bin/env python
# coding: utf-8

import argparse
import common
import conf
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for spp-nfv applicatino container")
    parser.add_argument(
        '-l', '--core-list',
        type=str,
        help="Core list")
    parser.add_argument(
        '-c', '--core-mask',
        type=str,
        help="Core mask")
    parser.add_argument(
        '-m', '--mem',
        type=int,
        default=1024,
        help="Memory size for spp_nfv")
    parser.add_argument(
        '--socket-mem',
        type=str,
        help="Memory size for spp_nfv")
    parser.add_argument(
        '-d', '--dev-id',
        type=int,
        help="vhost device ID")
    parser.add_argument(
        '-n', '--nof-memchan',
        type=int,
        default=4,
        help="Port of SPP controller")
    parser.add_argument(
        '--container-name',
        type=str,
        default='spp-container',
        help="Name of container image")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        common.error_exit('--core-mask or --core-list')

    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    if args.dev_id is None:
        common.error_exit('--dev-id')

    sock_host = '/tmp/sock%d' % args.dev_id
    sock_guest = '/var/run/usvhost%d' % args.dev_id

    docker_cmd = [
        'sudo', 'docker', 'run', '-it', '\\',
        '-v', '%s:%s' % (sock_host, sock_guest), '\\',
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        conf.spp_container, '\\'
    ]

    cmd_path = 'testpmd'

    testpmd_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'auto', '\\',
        '--no-pci', '\\',
        '--vdev', 'virtio_user%d,path=%s' % (args.dev_id, sock_guest), '\\',
        '--file-prefix', 'testpmd%d' % args.dev_id, '\\',
        '--', '\\',
        '-i', '\\',
        '--txqflags', '0xf00', '\\',
        '--disable-hw-vlan'
    ]

    cmds = docker_cmd + testpmd_cmd
    common.print_pretty_commands(cmds)

    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
