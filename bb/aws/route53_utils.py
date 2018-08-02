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


def create_or_update_dns_a_record(name,
                                  zone_prefix,
                                  zone_dns,
                                  ip_address,
                                  zone_id=None,
                                  region=None):
    """Create A record for provided details

    Parameters
    ----------
        name: str
            prefix for the provided zone
        zone_prefix: str
            zone prefix
        zone_dns: str
            hosted zone DNS
        zone_id: str
            hosted zone id (can be left as `None`)
        ip_address: str
            ip_address for the A record
        region: str
            AWS region name (optional)
    Returns
    -------
    A `dict` of EC2 instances

    """
    dns_name = ''
    if zone_prefix is not None:
        if zone_prefix.endswith('.'):
            zone_prefix = zone_prefix[:-1]
        dns_name = name + '.' + zone_prefix + '.' + zone_dns
    else:
        dns_name = name + '.' + zone_dns
    log.debug(
        'Create or update A record: [ %s = %s ]',
        dns_name,
        ip_address)
    client = aws_client_factory.get_route53_client(region)

    if zone_id is None:
        log.debug(
            'Retrieve HostedZone ID based upon name: [%s] from Route53',
            zone_dns)
        zone_id = get_hosted_zone_id(zone_dns, region)

    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': ip_address
                            },
                        ]
                    }
                },
            ]
        }
    )
    return response['ChangeInfo']['Status']


def get_hosted_zone_id(zone_dns, region=None):
    """Retrive the hosted zone id give the provided zone DNS name

    Parameters
    ----------
        prefix: str
            prefix for the provided zone
        zone_dns: str
            hosted zone DNS
        region: str
            AWS region name (optional)
    Returns
    -------
    A `str` with the hosted zone ID populated

    """
    log.debug(
        'Get the HostedZoneId [%s]',
        zone_dns)
    client = aws_client_factory.get_route53_client(region)
    response = client.list_hosted_zones_by_name(
        DNSName=zone_dns,
        MaxItems='1')

    return response['HostedZones'][0]['Id']
