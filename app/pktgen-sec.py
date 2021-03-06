#!/usr/bin/env python
# coding: utf-8

import argparse
import common
import conf
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for pktgen-sec application container")
    parser.add_argument(
        '-l', '--core-list',
        type=str,
        help="Core list, required two or more")
    parser.add_argument(
        '-c', '--core-mask',
        type=str,
        help="Core mask, required two or more")
    parser.add_argument(
        '-m', '--mem',
        type=int,
        default=1024,
        help="Memory size for application")
    parser.add_argument(
        '--socket-mem',
        type=str,
        help="Memory size for application")
    parser.add_argument(
        '-d', '--dev-ids',
        type=str,
        help="ring device IDs")
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
        '--matrix',
        type=str,
        help="Matrix of cores and port, [1:2].0 or 1.0 or so")
    parser.add_argument(
        '--blacklists',
        type=str,
        help="Blacklists, exp, '0000:2a:00.0,0000:2a:00.1'")
    parser.add_argument(
        '--log-level',
        type=int,
        default=7,
        help="pktgen-dpdk log level")
    return parser.parse_args()


def cores_to_range(core_opt):
    """Expand cores to ranged list.

    For exp, '1-3,5' is converted to [1,2,3,5],
    or '0x17' is to [1,2,3,5].
    """

    res = []
    if core_opt['attr'] == '-c':
        bin_list = list(
            format(
                int(core_opt['val'], 16), 'b'))
        cnt = 1
        bin_list.reverse()
        for i in bin_list:
            if i == '1':
                res.append(cnt)
            cnt += 1
    elif core_opt['attr'] == '-l':
        for core_part in core_opt['val'].split(','):
            if '-' in core_part:
                cl = core_part.split('-')
                res = res + range(int(cl[0]), int(cl[1])+1)
            else:
                res.append(int(core_part))
    else:
        pass
    res = common.uniq(res)
    res.sort()
    return res


def main():
    args = parse_args()

    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        common.error_exit('core_mask or core_list')

    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    if args.dev_ids is None:
        common.error_exit('--dev-ids')

    if args.matrix is not None:
        matrix = args.matrix
    else:
        port_id = 0
        core_range = cores_to_range(core_opt)
        if len(core_range) < 2:
            print("Error: Two or more cores required!")
            exit()
        elif len(core_range) == 2:
            matrix = '%d.%d' % (core_range[1], port_id)
        else:
            matrix = '[%d:%d].%d' % (core_range[1], core_range[2], port_id)

    # pktgen theme
    theme_file = 'themes/white-black.theme'

    docker_cmd = [
        'sudo', 'docker', 'run', '-it', '\\',
        '--privileged', '\\',
        '--workdir', '%s/../pktgen-dpdk' % conf.RTE_SDK, '\\',
        # '-v', '%s:%s' % (sock_host, sock_guest), '\\',
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        '-v', '/var/run/:/var/run/', '\\',
        '-v', '/tmp/:/tmp/', '\\',
        conf.spp_container, '\\'
    ]

    cmd_path = '%s/../pktgen-dpdk/app/%s/pktgen' % (
        conf.RTE_SDK, conf.RTE_TARGET)

    pktgen_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'secondary', '\\']

    for dev_id in common.dev_ids_to_list(args.dev_ids):
        pktgen_cmd += ['--vdev', 'net_ring%d' % dev_id, '\\']

    for bl in args.blacklists.split(','):
        pktgen_cmd += ['-b', bl, '\\']

    pktgen_cmd += [
        '--log-level', str(args.log_level), '\\',
        '--', '\\',
        '-T', '\\',
        '-P', '\\',
        '-m', matrix, '\\',
        '-f', theme_file
    ]

    cmds = docker_cmd + pktgen_cmd
    common.print_pretty_commands(cmds)

    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
