#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import boto3
import logging

from . import region_utils as aws_region

log = logging.getLogger(__name__)


def get_asg_client(region: str = None) -> object:
    """Get boto3 asg client

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    AutoScaling client
    """
    return __get_client('autoscaling', region)


def get_ec2_client(region: str = None) -> object:
    """Get boto3 ec2 client

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    return __get_client('ec2', region)


def get_ec2_resource(region: str = None) -> object:
    """Get boto3 ec2 resource

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 resource
    """
    return __get_resource('ec2', region)


def get_s3_client(region: str = None) -> object:
    """Get boto3 s3 client

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    return __get_client('s3', region)


def get_s3_resource(region: str = None) -> object:
    """Get boto3 s3 resource

    Parameters
    ----------
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    return __get_resource('s3', region)


def __get_client(service, region):
    """Get boto3 service client

    Parameters
    ----------
        service: str
            AWS service
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    if region is None:
        region = aws_region.get_region()
    return boto3.client(service, region_name=region)


def __get_resource(service, region):
    """Get boto3 service resource

    Parameters
    ----------
        service: str
            AWS service
        region: str
            AWS region (optional)
    Returns
    -------
    ec2 client
    """
    if region is None:
        region = aws_region.get_region()
    return boto3.resource(service, region_name=region)
