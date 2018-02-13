#!/usr/bin/env python
# coding: utf-8

import argparse
import common
import conf
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for l2fwd application container")
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
        help="Memory size")
    parser.add_argument(
        '--socket-mem',
        type=str,
        help="Memory size for NUMA nodes")
    parser.add_argument(
        '-d', '--dev-ids',
        type=str,
        help='two or more even vhost device IDs')
    parser.add_argument(
        '-n', '--nof-memchan',
        type=int,
        default=4,
        help="Number of memory channels")
    parser.add_argument(
        '-p', '--port-mask',
        type=str,
        help="Port mask")
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
        help="Print matrix for checking and exit. Do not run l2fwd")
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

    if args.port_mask is None:
        common.error_exit('--port-mask')

    # This container is running in backgroud in defualt.
    if args.foreground is not True:
        docker_run_opt = '-d'
    else:
        docker_run_opt = '-it'

    # Parse vhost device IDs and Check the number of devices is sufficient
    # for port mask.
    dev_ids = common.dev_ids_to_list(args.dev_ids)
    if common.is_sufficient_dev_ids(dev_ids, args.port_mask) is not True:
        print("Error: Cannot reserve ports '%s (= 0b%s)' on devices '%s'." % (
            args.port_mask, format(int(args.port_mask, 16), 'b'), dev_ids))
        exit()

    # Check if the number of ports is even for l2fwd.
    nof_ports = common.count_ports(args.port_mask)
    if (nof_ports % 2) != 0:
        print("Error: Number of ports must be an even number!")
        exit()

    # Setup for vhost devices with given device IDs.
    socks = []
    for dev_id in dev_ids:
        socks.append({
            'host': '/tmp/sock%d' % dev_id,
            'guest': '/var/run/usvhost%d' % dev_id})

    # Setup docker command.
    docker_cmd = [
        'sudo', 'docker', 'run', docker_run_opt, '\\']

    for sock in socks:
        docker_cmd += [
            '-v', '%s:%s' % (sock['host'], sock['guest']), '\\']

    docker_cmd += [
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        conf.spp_container, '\\'
    ]

    # Setup l2fwd command run on container.
    cmd_path = '%s/examples/l2fwd/%s/l2fwd' % (conf.RTE_SDK, conf.RTE_TARGET)

    l2fwd_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'auto', '\\']

    for i in range(len(dev_ids)):
        l2fwd_cmd += [
            '--vdev', 'virtio_user%d,path=%s' % (
                dev_ids[i], socks[i]['guest']), '\\'
        ]

    l2fwd_cmd += [
        '--file-prefix', 'spp-l2fwd-container%d' % dev_ids[0], '\\',
        '--', '\\',
        '-p', args.port_mask
    ]

    cmds = docker_cmd + l2fwd_cmd
    common.print_pretty_commands(cmds)

    if args.dry_run is True:
        exit()

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
