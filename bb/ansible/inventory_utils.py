#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import logging

from collections import OrderedDict
from six import iteritems

from bb.utils import file_utils as file_util
from bb.aws import ec2_utils as ec2
from bb.aws import asg_utils as asg

log = logging.getLogger(__name__)


def create_inventory(groups):
    """ Create a fully formed ansible inventory dictionary from a `list` of
    groups. The `group` list can be formed using the `create_inventory_group`
    method in this package.

    Parameters
    ----------
        groups: `list` of group `dict`
            list of groups to form into an ansible dictionary

    Returns
    -------
    ansible inventory `dict` that can be printed using `json.dumps`
    """
    inv = {
        '_meta': {
            'hostvars': {}
        }
    }
    for g in groups:
        group = {
            'hosts': g['hosts']
        }
        # add children groups
        if len(g['children']) > 0:
            group['children'] = g['children']
        # add group to the inventory dictionary
        inv[g['name']] = group
        # add vars to _meta section as required
        if len(g['vars']) > 0:
            for host in g['hosts']:
                hostvars = {}
                for var in g['vars']:
                    for k, v in iteritems(var):
                        hostvars[k] = v
                inv['_meta']['hostvars'][host] = hostvars
    return inv


def create_inventory_group(name, host_list, vars=[], child_groups=[]):
    """ Create a group `dict` for use in the `create_inventory` method.

    Parameters
    ----------
        name: `str`
            name of the ansible inventory group
        host_list: `list`
            list of ip addresses or resolveable hostnames
        vars: `list`
            list of `dict` key/value pairs e.g. [{'foo':'bar'}] to be added
            as hostvars for the inventory group (optional)
        child_groups: `list`
            list of child group names for this inventory (optional)

    Returns
    -------
    group `dict` designed to be used in list passed to `create_inventory`
    """
    group = {
        'name': name,
        'hosts': host_list,
        'vars': vars,
        'children': child_groups
    }
    return group


def create_dynamic_ec2_inventory(definition_file, region=None):
    """ Create a fully formed ansible ec2 inventory dictionary based on the
    definition file.

    Parameters
    ----------
        definition_file: `file`
            filename of the definition yaml file
        region: `str`
            aws region

    Returns
    -------
    ansible inventory `dict` that can be printed using `json.dumps`

    Example definition file
    -----------------------
    ```
    ec2_inventory_groups:
      # list of Auto Scaling Groups using ASG Name (optional)
      asg_groups:
        # populate field with ASG Name
        - name: foo-auto-scaling-group
          inventory:
            # name of ansible inventory group
            name: foo_hosts
            # optional list of vars for ansible inventory group
            vars:
              - a: false
              - bar: yup
            # optional list of child ansible inventory groups
            children:
              - alpha_hosts
      # list of EC2 Groups using Name Tag (optional)
      ec2_groups:
        # populate field with EC2 Name query (could be exact match or wildcard)
        - name: alpha-web-servers-*
          inventory:
            name: alpha_hosts
    ```
    """
    inv = file_util.read_yaml_file(definition_file)
    log.debug('Definition File Contents: %s', inv)
    groups = []
    if 'ec2_groups' in inv['ec2_inventory_groups']:
        for g in inv['ec2_inventory_groups']['ec2_groups']:
            results = OrderedDict(
                sorted(
                    iteritems(ec2.get_ec2_instances(g['name'], region)),
                    key=lambda x: x[1]['Name']))
            if len(results) > 0:
                instances = [
                    v['PrivateIpAddress'] for k, v in iteritems(results)
                ]
                groups.append(
                    create_inventory_group(
                        g['inventory']['name'],
                        instances,
                        g['inventory'].get('vars', []),
                        g['inventory'].get('children', [])
                    )
                )

    if 'asg_groups' in inv['ec2_inventory_groups']:
        for g in inv['ec2_inventory_groups']['asg_groups']:
            results = OrderedDict(
                sorted(
                    iteritems(
                        ec2.get_ec2_instance_info(
                            asg.get_asg_ec2_instance_ids(g['name'], region))),
                    key=lambda x: x[1]['Name']))
            if len(results) > 0:
                instances = [
                    v['PrivateIpAddress'] for k, v in iteritems(results)
                ]
                groups.append(
                    create_inventory_group(
                        g['inventory']['name'],
                        instances,
                        g['inventory'].get('vars', []),
                        g['inventory'].get('children', [])
                    )
                )
    return create_inventory(groups)
