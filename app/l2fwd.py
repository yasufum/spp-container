#!/usr/bin/env python
# coding: utf-8

import argparse
import conf
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launcher for spp-nfv applicatino container")
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
        '-d', '--dev-ids',
        type=str,
        help='two or more even vhost device IDs')
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
        '-fg', '--foreground',
        action='store_true',
        help="Run container as foreground mode")
    return parser.parse_args()


def dev_ids_to_list(dev_ids):
    res = []
    for dev_id_part in dev_ids.split(','):
        if '-' in dev_id_part:
            cl = dev_id_part.split('-')
            res = res + range(int(cl[0]), int(cl[1])+1)
        else:
            res.append(int(dev_id_part))
    return res


def print_pretty_commands(cmds):
    print(' '.join(cmds).replace('\\', '\\\n'))


def error_exit(objname):
    print('Error: \'%s\' is not defined.' % objname)
    exit()


def main():
    args = parse_args()

    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        error_exit('--core-mask or --core-list')

    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    if args.dev_ids is None:
        error_exit('--dev-ids')

    if args.foreground is not True:
        docker_run_opt = '-d'
    else:
        docker_run_opt = '-it'

    dev_ids = dev_ids_to_list(args.dev_ids)
    if (len(dev_ids) % 2) != 0:
        print("Error: dev_ids must be an even number!")
        exit()

    print(dev_ids)
    exit()

    socks = []
    for dev_id in dev_ids:
        socks.append({
            'host': '/tmp/sock%d' % dev_id,
            'guest': '/var/run/usvhost%d' % dev_id})

    docker_cmd = [
        'sudo', 'docker', 'run', docker_run_opt, '\\']

    for sock in socks:
        docker_cmd += [
            '-v', '%s:%s' % (sock['host'], sock['guest']), '\\']

    docker_cmd += [
        '-v', '/dev/hugepages:/dev/hugepages', '\\',
        '-v', '/var/run/:/var/run/', '\\',
        conf.spp_container, '\\'
    ]

    cmd_path = '%s/examples/l2fwd/%s/l2fwd' % (conf.RTE_SDK, conf.RTE_TARGET)

    spp_cmd = [
        cmd_path, '\\',
        core_opt['attr'], core_opt['val'], '\\',
        '-n', str(args.nof_memchan), '\\',
        mem_opt['attr'], mem_opt['val'], '\\',
        '--proc-type', 'primary', '\\']
    for dev_id in dev_ids:
        spp_cmd += [
            '--vdev', 'virtio_user%d,path=%s' % (dev_id, socks['guest']), '\\']

        '--file-prefix', 'spp-vm%d' % args.dev_id, '\\',
        '--', '\\',
        '-n', str(args.sec_id)
    ]

    cmds = docker_cmd + spp_cmd
    print_pretty_commands(cmds)

    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
