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
        help="Core list, required two or more")
    parser.add_argument(
        '-c', '--core-mask',
        type=str,
        help="Core mask, required two or more")
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
        '-d', '--dev-ids',
        type=str,
        help="vhost device IDs")
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
    parser.add_argument(
        '--matrix',
        type=str,
        help="matrix of cores and port, [1:2].0 or 1.0 or so")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Print matrix for checking and exit. Do not run pktgen-dpdk")
    parser.add_argument(
        '--log-level',
        type=int,
        default=7,
        help="pktgen-dpdk log level")
    return parser.parse_args()


def main():
    args = parse_args()

    # Check core_mask or core_list is defined.
    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        common.error_exit('core_mask or core_list')

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

    # Setup matrix for assignment of cores and ports.
    if args.matrix is not None:
        matrix = args.matrix
    else:
        # Get core_list such as [0,1,2] from '-c 0x07' or '-l 0-2'
        core_list = common.cores_to_list(core_opt)
        if len(core_list) < 2:
            print("Error: Two or more cores required for master and slave!")
            exit()

        slave_core_list = core_list[1:]
        nof_slave_cores = len(slave_core_list)
        nof_ports = len(dev_ids)
        nof_cores_each_port = nof_slave_cores / nof_ports
        if nof_cores_each_port < 1:
            print("Error: Too few cores for given port(s)!")
            print("%d cores required for %d port(s)" % (
                (nof_slave_cores + 1), nof_ports))
            exit()

        matrix_list = []
        if nof_cores_each_port == 1:
            for i in range(0, nof_ports):
                matrix_list.append('%d.%d' % (slave_core_list[i], i))
        elif nof_cores_each_port == 2:
            for i in range(0, nof_ports):
                matrix_list.append('[%d:%d].%d' % (
                    slave_core_list[2*i], slave_core_list[2*i + 1], i))
        elif nof_cores_each_port == 3:  # Give two cores for rx and one for tx.
            for i in range(0, nof_ports):
                matrix_list.append('[%d-%d:%d].%d' % (
                    slave_core_list[3*i],
                    slave_core_list[3*i + 1],
                    slave_core_list[3*i + 2], i))
        elif nof_cores_each_port == 4:
            for i in range(0, nof_ports):
                matrix_list.append('[%d-%d:%d-%d].%d' % (
                    slave_core_list[4*i],
                    slave_core_list[4*i + 1],
                    slave_core_list[4*i + 2],
                    slave_core_list[4*i + 3], i))
        # Do not support more than five because it is rare case and
        # calculation is complex.
        else:
            print("Error: Too many cores for calculation for port assignment!")
            print("Please consider to use '--matrix' for assigning directly")
            exit()
        matrix = ','.join(matrix_list)

    # pktgen theme
    theme_file = 'themes/white-black.theme'

    # Setup docker command.
    docker_cmd = [
        'sudo', 'docker', 'run', '-it', '\\',
        '--workdir', '%s/../pktgen-dpdk' % conf.RTE_SDK, '\\']
    for sock in socks:
        docker_cmd += [
            '-v', '%s:%s' % (sock['host'], sock['guest']), '\\']

    docker_cmd += [
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        conf.spp_container, '\\']

    cmd_path = '%s/../pktgen-dpdk/app/%s/pktgen' % (
        conf.RTE_SDK, conf.RTE_TARGET)

    # Setup pktgen command.
    pktgen_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'auto', '\\']

    for i in range(len(dev_ids)):
        pktgen_cmd += [
            '--vdev', 'virtio_user%d,path=%s' % (
                dev_ids[i], socks[i]['guest']), '\\']

    pktgen_cmd += [
        '--file-prefix', 'pktgen-container%d' % dev_ids[0], '\\',
        '--log-level', str(args.log_level), '\\',
        '--', '\\',
        '-T', '\\',
        '-P', '\\',
        '-m', matrix, '\\',
        '-f', theme_file
    ]

    cmds = docker_cmd + pktgen_cmd
    common.print_pretty_commands(cmds)

    if args.dry_run is True:
        exit()

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
