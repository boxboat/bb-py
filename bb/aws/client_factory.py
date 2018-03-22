#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import boto3
import logging

log = logging.getLogger(__name__)


def get_default_region():
    """Get default region

    Requires user to have default region configured
    Returns
    -------
    The default AWS region
    """
    return boto3.session.Session().region_name


def get_asg_client(region):
    """Get boto3 asg client

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    AutoScaling client
    """
    if region is None:
        region = get_default_region()
    return boto3.client('autoscaling', region_name=region)


def get_ec2_client(region):
    """Get boto3 ec2 client

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    if region is None:
        region = get_default_region()
    return boto3.client('ec2', region_name=region)


def get_ec2_resource(region):
    """Get boto3 ec2 resource

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 resource
    """
    if region is None:
        region = get_default_region()
    return boto3.resource('ec2', region_name=region)
