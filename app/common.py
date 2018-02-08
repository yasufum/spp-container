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


def uniq(dup_list):
    """Remove duplicated elements in a list and return a unique list

    Example: [1,1,2,2,3,3] #=> [1,2,3]
    """

    return list(set(dup_list))
