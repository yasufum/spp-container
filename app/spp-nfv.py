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

container_name = 'spp'


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for spp-nfv application container")
    parser.add_argument(
        '-i', '--sec-id',
        type=int,
        help='Secondary ID')
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
        default=6666,
        help="Port of SPP controller")
    parser.add_argument(
        '--nof-memchan',
        type=int,
        default=4,
        help="Number of memory channels")
    parser.add_argument(
        '--container-name',
        type=str,
        default='spp-container',
        help="Name of container image")
    parser.add_argument(
        '-fg', '--foreground',
        action='store_true',
        help="Run container as foreground mode")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Print matrix for checking and exit. Do not run spp_nfv")
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
    if args.sec_id is None:
        common.error_exit('--sec-id')

    # This container is running in backgroud in defualt.
    if args.foreground is not True:
        docker_run_opt = '-d'
    else:
        docker_run_opt = '-it'

    # IP address of SPP controller.
    ctrl_ip = os.getenv('SPP_CTRL_IP', args.ctrl_ip)
    if ctrl_ip is None:
        common.error_exit('SPP_CTRL_IP')

    # Setup docker command.
    docker_cmd = [
        'sudo', 'docker', 'run', docker_run_opt, '\\',
        '--privileged', '\\',
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        '-v', '/var/run/:/var/run/', '\\',
        '-v', '/tmp/:/tmp/', '\\',
        env.CONTAINER_NAME[container_name], '\\'
    ]

    # Setup spp_nfv command.
    cmd_path = '%s/../spp/src/nfv/%s/spp_nfv' % (
        env.RTE_SDK, env.RTE_TARGET)

    spp_cmd = [cmd_path, '\\']

    eal_opts = [
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'secondary', '\\',
        '--', '\\']

    spp_opts = [
        '-n', str(args.sec_id), '\\',
        '-s', '%s:%d' % (ctrl_ip, args.ctrl_port)
    ]

    cmds = docker_cmd + spp_cmd + eal_opts + spp_opts
    common.print_pretty_commands(cmds)

    if args.dry_run is True:
        exit()

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
