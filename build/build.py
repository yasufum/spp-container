#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import subprocess
import sys

work_dir = os.path.dirname(__file__)
sys.path.append(work_dir + '/../app')
import common
import conf


def parse_args():
    parser = argparse.ArgumentParser(
        description="Docker image builder for SPP")
    parser.add_argument(
        '-n', '--container-name',
        type=str,
        help="Container name")
    parser.add_argument(
        '--dpdk-repo',
        type=str,
        default="http://dpdk.org/git/dpdk",
        help="Git url of DPDK")
    parser.add_argument(
        '--dpdk-branch',
        type=str,
        help="Specific branch for cloning DPDK")
    parser.add_argument(
        '--pktgen-repo',
        type=str,
        default="http://dpdk.org/git/apps/pktgen-dpdk",
        help="Git url of pktgen-dpdk")
    parser.add_argument(
        '--pktgen-branch',
        type=str,
        help="Specific branch for cloning pktgen-dpdk")
    parser.add_argument(
        '--spp-repo',
        type=str,
        default="http://dpdk.org/git/apps/spp",
        help="Git url of SPP")
    parser.add_argument(
        '--spp-branch',
        type=str,
        help="Specific branch for cloning SPP")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Print matrix for checking and exit. Do not run docker build")
    return parser.parse_args()


def create_env_sh(work_dir):
    """Create config file for DPDK environment variables

    Create 'env.sh' which defines $RTE_SDK and $RTE_TARGET inside a
    container to be referredd from 'run.sh' and Dockerfile.
    """
    contents = "export RTE_SDK=%s\n" % conf.RTE_SDK
    contents += "export RTE_TARGET=%s" % conf.RTE_TARGET

    f = open('%s/env.sh' % work_dir, 'w')
    f.write(contents)
    f.close()


def main():
    args = parse_args()

    # Check if container's name is given.
    if args.container_name is not None:
        container_name = args.container_name
    else:
        container_name = conf.spp_container

    # Setup branches if user specifies.
    if args.dpdk_branch is not None:
        dpdk_branch = "-b %s" % args.dpdk_branch
    else:
        dpdk_branch = ''

    if args.pktgen_branch is not None:
        pktgen_branch = "-b %s" % args.pktgen_branch
    else:
        pktgen_branch = ''

    if args.spp_branch is not None:
        spp_branch = "-b %s" % args.spp_branch
    else:
        spp_branch = ''

    # Setup environment variables on host to pass 'docker build'.
    env_opts = [
        'http_proxy',
        'https_proxy',
        'no_proxy'
    ]

    docker_cmd = ['sudo', 'docker', 'build', '\\']

    for opt in env_opts:
        if opt in os.environ.keys():
            docker_cmd += [
                '--build-arg', '%s=%s' % (opt, os.environ[opt]), '\\']

    docker_cmd += [
        '--build-arg', 'home_dir=%s' % conf.HOMEDIR, '\\',
        '--build-arg', 'rte_sdk=%s' % conf.RTE_SDK, '\\',
        '--build-arg', 'rte_target=%s' % conf.RTE_TARGET, '\\',
        '--build-arg', 'dpdk_repo=%s' % args.dpdk_repo, '\\',
        '--build-arg', 'dpdk_branch=%s' % dpdk_branch, '\\',
        '--build-arg', 'pktgen_repo=%s' % args.pktgen_repo, '\\',
        '--build-arg', 'pktgen_branch=%s' % pktgen_branch, '\\',
        '--build-arg', 'spp_repo=%s' % args.spp_repo, '\\',
        '--build-arg', 'spp_branch=%s' % spp_branch, '\\',
        '-t', container_name, work_dir
    ]

    common.print_pretty_commands(docker_cmd)

    if args.dry_run is True:
        exit()

    create_env_sh(work_dir)

    # Remove delimiters for print_pretty_commands().
    while '\\' in docker_cmd:
        docker_cmd.remove('\\')
    subprocess.call(docker_cmd)


if __name__ == '__main__':
    main()
