def uniq(dup_list):
    """Remove duplicated elements in a list and return a unique list

    Example: [1,1,2,2,3,3] #=> [1,2,3]
    """

    return list(set(dup_list))


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


def cores_to_list(core_opt):
    """Expand DPDK core option to ranged list.

    Core option must be a hash of attritute and its value.
    Attribute is -c(core mask) or -l(core list).
    For example, '-c 0x03' is described as:
      core_opt = {'attr': '-c', 'val': '0x03'}
    or '-l 0-1' is as
      core_opt = {'attr': '-l', 'val': '0-1'}

    Returned value is a list, such as:
      '0x17' is converted to [1,2,3,5].
    or
      '-l 1-3,5' is converted to [1,2,3,5],
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
    res = uniq(res)
    res.sort()
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
