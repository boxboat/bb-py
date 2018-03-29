#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import logging

from six import iteritems
from . import client_factory as aws_client_factory

log = logging.getLogger(__name__)


def get_asg_name(instance_id, region=None):
    """Get the asg name associated with this instance id (if one exists).

    Parameters
    ----------
        instance_id: str
            The instance_id to look for
        region: str
            AWS region name (optional)
    Returns
    -------
    The ASG name or None

    """
    log.debug('Retrieve ASG containing instance: %s', instance_id)
    client = aws_client_factory.get_asg_client(region)
    next_token = ''
    asgs = []
    while next_token is not None:
        kwargs = {}
        if next_token != '':
            kwargs = {'NextToken': next_token}
        response = client.describe_auto_scaling_groups(**kwargs)
        next_token = response.get('NextToken', None)
        asgs += response['AutoScalingGroups']

    for asg in asgs:
        for instance in asg['Instances']:
            if instance_id in [x for v in iteritems(instance) for x in v]:
                log.debug('Found ASG: %s', asg['AutoScalingGroupName'])
                return asg['AutoScalingGroupName']
    return None


def get_asg_desired_size(asg_name, region=None):
    """Get desired size of provided asg.

    Parameters
    ----------
        asg_name: str
            Name of the auto scaling group
        region: str
            AWS region name (optional)
    Returns
    -------
    Desired size of ASG
    """
    log.debug('Retrieve %s desired capacity')
    client = aws_client_factory.get_asg_client(region)
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            asg_name,
        ]
    )
    if len(response['AutoScalingGroups']) != 1:
        raise Exception(asg_name + ' not found')
    capacity = response['AutoScalingGroups'][0]['DesiredCapacity']
    log.debug('%s desired capacity: %s', asg_name, capacity)
    return capacity


def get_asg_ec2_instance_ids(asg_name, region=None):
    """Get list of instance-ids that are InService for provided Auto Scaling
    Group name.

    Parameters
    ----------
        asg_name: str
            Name of the auto scaling group
        region: str
            AWS region name (optional)
    Returns
    -------
    A list of EC2 instance-ids

    """
    client = aws_client_factory.get_asg_client(region)
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            asg_name,
        ]
    )
    if len(response['AutoScalingGroups']) != 1:
        raise Exception(asg_name + ' not found')
    instances = []
    for i in response['AutoScalingGroups'][0]['Instances']:
        if (i['LifecycleState'] == 'InService'):
            instances.append(i['InstanceId'])
    log.debug('Found %s with instances: %s', asg_name, instances)
    return instances
