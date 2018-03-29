#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import logging
import requests

from . import client_factory as aws_client_factory

log = logging.getLogger(__name__)


def get_instance_id():
    """ Retrieve the EC2 instance id from the instance-data url for instance
    this method is called from.

    Returns
    -------
    instance-id of current instance
    """
    log.debug('Get instance-id for current instance')
    id_request = requests.get(
        'http://instance-data/latest/meta-data/instance-id'
    )
    if id_request.status_code != 200:
        raise Exception(
            'Unable to retrieve instance-id, Response: %s %s',
            id_request.status_code,
            id_request.text
        )
    log.debug('Return instance-id: %s', id_request.text)
    return id_request.text


def get_instance_vpc_id():
    """ Retrieve the EC2 vpc id from the instance-data url for instance this
    method is called from.

    Returns
    -------
    vpc-id of current instance
    """
    log.debug('Get instance vpc-id for current instance')
    macs_request = requests.get(
        'http://instance-data/latest/meta-data/network/interfaces/macs/'
    )
    if macs_request.status_code != 200:
        raise Exception(
            'Unable to retrieve macs, Response: %s %s',
            macs_request.status_code,
            macs_request.text
        )
    mac = macs_request.text
    vpc_id_request = requests.get(
        'http://instance-data/latest/meta-data/network/interfaces/macs/'
        + mac
        + 'vpc-id'
    )
    if vpc_id_request.status_code != 200:
        raise Exception(
            'Unable to retrieve vpc-id, Response: %s %s',
            vpc_id_request.status_code,
            vpc_id_request.text
        )
    log.debug('Return vpc-id: %s', vpc_id_request.text)
    return vpc_id_request.text


def get_vpc_id_using_vpc_name(vpc_name, region=None):
    """ Retrieve the EC2 vpc id for provided vpc_name

    Returns
    -------
    vpc-id matching vpc_name
    """
    log.debug('Retrieving vpc-id: %s', vpc_name)
    resource = aws_client_factory.get_ec2_resource(region)
    vpc_list = list(
        resource.vpcs.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        vpc_name,
                    ]
                },
            ]
        )
    )
    if len(vpc_list) == 1:
        return vpc_list[0].id
    else:
        log.warn('No exact match found for %s', vpc_name)
        return None


def get_ec2_instances_in_vpc(vpc_id, region=None):
    """Get `dict` of ec2 instances in provided vpc

    Parameters
    ----------
        vpc_id: str
            vpc-id to retrieve instances from
        region: str
            AWS region name (optional)
    Returns
    -------
    A `dict` of EC2 instances

    """
    log.debug('Retrieving EC2 instances in vpc: %s', vpc_id)
    client = aws_client_factory.get_ec2_client(region)
    reservations = []
    next_token = ''
    while next_token is not None:
        kwargs = {
            'Filters': [
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id
                    ],
                }
            ]
        }
        if next_token != '':
            kwargs['NextToken'] = next_token
        response = client.describe_instances(**kwargs)
        next_token = response.get('NextToken', None)
        reservations += response['Reservations']
    return __parse_reservation_info(reservations)


def get_ec2_instances(name, region=None):
    """Get `dict` of ec2 instances matching provided name

    Parameters
    ----------
        name: str
            Name of the ec2 instance
        region: str
            AWS region name (optional)
    Returns
    -------
    A `dict` of EC2 instances

    """
    log.debug('Retrieving EC2 instances matching name: %s', name)
    client = aws_client_factory.get_ec2_client(region)
    instances = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name,
                ]
            },
        ]
    )
    return __parse_reservation_info(instances['Reservations'])


def get_ec2_instance_info(instance_ids, region=None):
    """Get `dict` of ec2 instances matching provided instance-ids

    Parameters
    ----------
        name: list
            List of ec2 instance ids
        region: str
            AWS region name (optional)
    Returns
    -------
    A `dict` of EC2 instances

    """
    log.debug('Retrieving EC2 instances: %s', instance_ids)
    client = aws_client_factory.get_ec2_client(region)
    instances = client.describe_instances(
        InstanceIds=instance_ids
    )
    return __parse_reservation_info(instances['Reservations'])


def set_ec2_instance_name(instance_id, name, region=None):
    """Set the ec2 instance name tag

    Parameters
    ----------
        instance_id: str
            Instance id to set name tag on
        name: str
            New instance name
        region: str
            AWS region name (optional)
    Returns
    -------
    None

    """
    log.debug('Setting EC2 instance: %s name: %s', instance_id, name)
    client = aws_client_factory.get_ec2_client(region)
    client.create_tags(
        Resources=[
            instance_id,
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': name
            },
        ]
    )


def __parse_reservation_info(reservations):
    info = {}
    for r in reservations:
        for i in r['Instances']:
            name = ''
            for tag in i['Tags']:
                if tag['Key'] == 'Name':
                    name = tag['Value']
            info[i['InstanceId']] = {
                'Tags': i['Tags'],
                'AvailabilityZone': i['Placement']['AvailabilityZone'],
                'PrivateIpAddress': i['PrivateIpAddress'],
                'PrivateDnsName': i['PrivateDnsName'],
                'PublicDnsName': i.get('PublicDnsName', None),
                'PublicIpAddress': i.get('PublicIpAddress', None),
                'VpcId': i['VpcId'],
                'SubnetId': i['SubnetId'],
                'State': i['State']['Name'],
                'Name': name,
            }
    log.debug('EC2 instance info: %s', info)
    return info
