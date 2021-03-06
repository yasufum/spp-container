#!/usr/bin/env python
# coding: utf-8

import argparse
import common
import conf
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for load-balancer application container")
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
        '-rx', '--rx-ports',
        type=str,
        help="List of rx ports and queues handled by the I/O rx lcores")
    parser.add_argument(
        '-tx', '--tx-ports',
        type=str,
        help="List of tx ports and queues handled by the I/O tx lcores")
    parser.add_argument(
        '-w', '--worker-lcores',
        type=str,
        help="List of worker lcores")
    parser.add_argument(
        '-rsz', '--ring-sizes',
        type=str,
        help="Ring sizes of 'rx_read,rx_send,w_send,tx_written'")
    parser.add_argument(
        '-bsz', '--burst-sizes',
        type=str,
        help="Burst sizes of rx, worker or tx")
    parser.add_argument(
        '--lpm',
        type=str,
        help="List of LPM rules")
    parser.add_argument(
        '--pos-lb',
        type=int,
        help="Position of the 1-byte field used for identify worker")
    parser.add_argument(
        '-fg', '--foreground',
        action='store_true',
        help="Run container as foreground mode")
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

    if args.rx_ports is None:
        common.error_exit('--rx-ports')
    if args.tx_ports is None:
        common.error_exit('--tx-ports')
    if args.worker_lcores is None:
        common.error_exit('--worker-lcores')
    if args.lpm is None:
        common.error_exit('--lpm')

    # This container is running in backgroud in defualt.
    if args.foreground is not True:
        docker_run_opt = '-d'
    else:
        docker_run_opt = '-it'

    # Setup for vhost devices with given device IDs.
    dev_ids = common.dev_ids_to_list(args.dev_ids)
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

    app_name = 'load_balancer'
    cmd_path = '%s/examples/%s/%s/%s' % (
        conf.RTE_SDK, app_name, conf.RTE_TARGET, app_name)

    # Setup testpmd command.
    lb_cmd = [cmd_path, '\\']

    eal_opts = [
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'auto', '\\']

    for i in range(len(dev_ids)):
        eal_opts += [
            '--vdev', 'virtio_user%d,path=%s' % (
                dev_ids[i], socks[i]['guest']), '\\']

    eal_opts += [
        '--file-prefix', '%s%d' % (app_name, dev_ids[0]), '\\',
        '--', '\\']

    lb_opts = []
    if args.ring_sizes is not None:
        lb_opts += [
            '--ring-sizes', args.ring_sizes, '\\']
    if args.burst_sizes is not None:
        lb_opts += [
            '--burst-sizes', args.burst_sizes, '\\']
    if args.pos_lb is not None:
        lb_opts += [
            '--pos-lb', str(args.pos_lb)]

    rx_ports = '"%s"' % args.rx_ports
    tx_ports = '"%s"' % args.tx_ports
    worker_lcores = '"%s"' % args.worker_lcores
    lpm = '"%s"' % args.lpm
    lb_opts += [
        '--rx', rx_ports, '\\',
        '--tx', tx_ports, '\\',
        '--w', worker_lcores, '\\',
        '--lpm', lpm]

    cmds = docker_cmd + lb_cmd + eal_opts + lb_opts
    common.print_pretty_commands(cmds)

    if args.dry_run is True:
        exit()

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
