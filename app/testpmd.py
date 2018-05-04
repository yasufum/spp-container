#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import subprocess
import sys

work_dir = os.path.dirname(__file__)
sys.path.append(work_dir + '/..')
from conf import env
from lib import common

container_name = 'dpdk'


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for testpmd application container")
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
        help="Memory size for application, exp: -m 1024")
    parser.add_argument(
        '--socket-mem',
        type=str,
        help="Memory size for application, exp: --socket-mem 512,512")
    parser.add_argument(
        '-d', '--dev-ids',
        type=str,
        help="vhost device IDs")
    parser.add_argument(
        '-n', '--nof-memchan',
        type=int,
        default=4,
        help="Number of memory channels")
    parser.add_argument(
        '--container-name',
        type=str,
        default='spp-container',
        help="Name of container image")
    parser.add_argument(
        '--pci',
        action='store_true',
        help="Enable PCI (default is None)")
    parser.add_argument(
        '--enable-hw-vlan',
        action='store_true',
        help="Enable hardware vlan (default is None)")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Print matrix for checking and exit. Do not run testpmd")
    return parser.parse_args()


def main():
    args = parse_args()

    # Check core_mask or core_list is defined.
    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        common.error_exit('--core-mask or --core-list')

    # Check memory option is defined.
    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    # Check for other mandatory opitons.
    if args.dev_ids is None:
        common.error_exit('--dev-ids')

    # Setup for vhost devices with given device IDs.
    dev_ids = common.dev_ids_to_list(args.dev_ids)
    socks = []
    for dev_id in dev_ids:
        socks.append({
            'host': '/tmp/sock%d' % dev_id,
            'guest': '/var/run/usvhost%d' % dev_id})

    # Setup docker command.
    docker_cmd = [
        'sudo', 'docker', 'run', '-it', '\\']

    for sock in socks:
        docker_cmd += [
            '-v', '%s:%s' % (sock['host'], sock['guest']), '\\']

    docker_cmd += [
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        env.CONTAINER_NAME[container_name], '\\'
    ]

    cmd_path = 'testpmd'

    # Setup testpmd command.
    testpmd_cmd = [cmd_path, '\\']

    eal_opts = [
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'auto', '\\']

    if args.pci is False:
        eal_opts += ['--no-pci', '\\']

    for i in range(len(dev_ids)):
        eal_opts += [
            '--vdev', 'virtio_user%d,path=%s' % (
                dev_ids[i], socks[i]['guest']), '\\']

    eal_opts += [
        '--file-prefix', 'testpmd%d' % dev_ids[0], '\\',
        '--', '\\']

    testpmd_opts = []
    if args.enable_hw_vlan is True:
        testpmd_opts += ['--elable-hw-vlan', '\\']

    testpmd_opts += [
        '-i'
    ]

    cmds = docker_cmd + testpmd_cmd + eal_opts + testpmd_opts
    common.print_pretty_commands(cmds)

    if args.dry_run is True:
        exit()

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
