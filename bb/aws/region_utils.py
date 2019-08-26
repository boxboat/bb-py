#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import logging
import requests
import json
import boto3
import os

import bb.aws

log = logging.getLogger(__name__)


def __init_region():
    log.debug('Initializing region')
    region = None
    try:
        region = __get_default_region()
        if region is not None:
            __set_region(region)
    except Exception as e:
        log.warn(
            'No default region defined by user will attempt to use instance '
            'region %s',
            e)

    if region is None:
        try:
            __set_region(get_instance_region())
        except Exception as e:
            log.warn('Could not determine region automatically, set --region')
            exit(1)


def __get_default_region():
    """Get default region

    Requires user to have default region configured
    Returns
    -------
    The default AWS region
    """
    return boto3.session.Session().region_name


def __set_region(region_name):
    log.debug('Setting bb.aws.region: %s', region_name)
    bb.aws.region = region_name


def set_region(region_name):
    """Set region

    Parameters
    ----------
        region_name: `str`
            aws region
    """
    __set_region(region_name)


def get_region():
    """Get the aws region

    Returns
    ----------
    aws region `str`
    """
    if bb.aws.region is None:
        __init_region()
    log.debug('Return region: %s', bb.aws.region)
    return bb.aws.region


def get_instance_region():
    """ Retrieve the region from the instance-data url for instance this
    method is called from.

    Returns
    -------
    aws region of current instance
    """
    id_request = requests.get(
        'http://instance-data/latest/dynamic/instance-identity/document'
    )
    if id_request.status_code != 200:
        raise Exception(
            'Unable to retrieve instance-identity, Response: %s %s',
            id_request.status_code,
            id_request.text
        )
    json_response = json.loads(id_request.text)
    return json_response['region']
