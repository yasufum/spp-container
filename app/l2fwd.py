#!/usr/bin/env python
# coding: utf-8

import argparse
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
    return parser.parse_args()


def count_ports(port_mask):
    """Return the number of ports of given portmask"""

    ports_in_binary = format(int(port_mask, 16), 'b')
    nof_ports = ports_in_binary.count('1')
    return nof_ports


def dev_ids_to_list(dev_ids):
    """Parse vhost device IDs and return as a list.

    Example:
    '1,3-5' #=> [1,3,4,5]
    """

    res = []
    for dev_id_part in dev_ids.split(','):
        if '-' in dev_id_part:
            cl = dev_id_part.split('-')
            res = res + range(int(cl[0]), int(cl[1])+1)
        else:
            res.append(int(dev_id_part))
    return res


def print_pretty_commands(cmds):
    """Print given command in pretty format"""

    print(' '.join(cmds).replace('\\', '\\\n'))


def is_sufficient_dev_ids(dev_ids, port_mask):
    """Check if ports can be reserved for dev_ids

    Return true if the number of dev IDs equals or more than given ports.
    'dev_ids' a list of vhost device IDs such as [1,2,3].
    """

    if not ('0x' in port_mask):  # invalid port mask
        return False

    ports_in_binary = format(int(port_mask, 16), 'b')
    if len(dev_ids) >= len(ports_in_binary):
        return True
    else:
        return False


def error_exit(objname):
    """Print error message and exit

    This function is used for notifying an argument for the object
    is not given.
    """

    print('Error: \'%s\' is not defined.' % objname)
    exit()


def main():
    args = parse_args()

    # Check core_mask or core_list is defined.
    if args.core_mask is not None:
        core_opt = {'attr': '-c', 'val': args.core_mask}
    elif args.core_list is not None:
        core_opt = {'attr': '-l', 'val': args.core_list}
    else:
        error_exit('--core-mask or --core-list')

    # Check memory option is defined.
    if args.socket_mem is not None:
        mem_opt = {'attr': '--socket-mem', 'val': args.socket_mem}
    else:
        mem_opt = {'attr': '-m', 'val': str(args.mem)}

    # Check for other mandatory opitons.
    if args.dev_ids is None:
        error_exit('--dev-ids')

    if args.port_mask is None:
        error_exit('--port-mask')

    # This container is running in backgroud in defualt.
    if args.foreground is not True:
        docker_run_opt = '-d'
    else:
        docker_run_opt = '-it'

    # Parse vhost device IDs and Check the number of devices is sufficient
    # for port mask.
    dev_ids = dev_ids_to_list(args.dev_ids)
    if is_sufficient_dev_ids(dev_ids, args.port_mask) is not True:
        print("Error: Cannot reserve ports '%s (= 0b%s)' on devices '%s'." % (
            args.port_mask, format(int(args.port_mask, 16), 'b'), dev_ids))
        exit()

    # Check if the number of ports is even for l2fwd.
    nof_ports = count_ports(args.port_mask)
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
    print_pretty_commands(cmds)

    # Remove delimiters for print_pretty_commands().
    while '\\' in cmds:
        cmds.remove('\\')
    subprocess.call(cmds)


if __name__ == '__main__':
    main()
