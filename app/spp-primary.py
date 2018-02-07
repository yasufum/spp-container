#!/usr/bin/env python
# coding: utf-8

import argparse
import conf
import os
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for spp-nfv applicatino container")
    parser.add_argument(
        '-n', '--nof-ring',
        type=int,
        default=10,
        help='Maximum number of Ring PMD')
    parser.add_argument(
        '-p', '--port-mask',
        type=str,
        help='Port mask')
    parser.add_argument(
        '-l', '--core-list',
        type=str,
        help='Core list')
    parser.add_argument(
        '-c', '--core-mask',
        type=str,
        help='Core mask')
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
        '-ip', '--ctrl-ip',
        type=str,
        help="IP address of SPP controller")
    parser.add_argument(
        '--ctrl-port',
        type=int,
        default=5555,
        help="Port of SPP controller")
    parser.add_argument(
        '--nof-memchan',
        type=int,
        default=4,
        help="Port of SPP controller")
    parser.add_argument(
        '--container-name',
        type=str,
        default='spp-container',
        help="Name of container image")
    return parser.parse_args()


def print_pretty_commands(cmds):
    print(' '.join(cmds).replace('\\', '\\\n'))


def error_exit(objname):
    print('Error: \'%s\' is not defined.' % objname)
    exit()


def main():
    args = parse_args()

    if args.port_mask is None:
        error_exit('port_mask')

    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        error_exit('core_mask or core_list')

    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    ctrl_ip = os.getenv('SPP_CTRL_IP', args.ctrl_ip)
    if ctrl_ip is None:
        error_exit('SPP_CTRL_IP')

    docker_cmd = [
        'sudo', 'docker', 'run', '-it', '\\',
        '--privileged', '\\',
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        '-v', '/var/run/:/var/run/', '\\',
        conf.spp_container, '\\'
    ]

    cmd_path = '%s/../spp/src/primary/%s/spp_primary' % (
        conf.RTE_SDK, conf.RTE_TARGET)

    spp_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--huge-dir', '/dev/hugepages', '\\',
        '--proc-type', 'primary', '\\',
        '--', '\\',
        '-p', args.port_mask, '\\',
        '-n', str(args.nof_ring), '\\',
        '-s', '%s:%d' % (ctrl_ip, args.ctrl_port)
    ]

    cmds = docker_cmd + spp_cmd
    print_pretty_commands(cmds)

    while '\\' in cmds:
        cmds.remove('\\')

    subprocess.call(cmds)


if __name__ == '__main__':
    main()
