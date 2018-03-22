#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import os
import logging
import argparse
import json
import bb

from bb.ansible import inventory_utils as inv_util
from bb.aws import ec2_utils as ec2


def setup_logging(log_level=logging.INFO):
    format_string = '%(asctime)s %(name)s [%(levelname)s] %(message)s'
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    bb.set_stream_handler(log_level, format_string)


def main():
    description = (
        'Ansible VPC Dynamic Inventory - set VPC_ID or VPC_NAME in the '
        'environment and this script will generate a dynamic inventory '
        'of all running ec2 instances. Note: if environment variables '
        'are not set, then the vpc of the instance this playbook is '
        'executed on will be used. If both are set and they conflict '
        'this script will exit.')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--list',
        action='store_true',
        help='Print ansible dynamic inventory')
    parser.add_argument('--host')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debugging output'
    )
    args = parser.parse_args()

    if args.debug:
        setup_logging(logging.DEBUG)

    log = logging.getLogger(__name__)

    # determine region
    region = os.getenv('AWS_DEFAULT_REGION')
    if not region:
        region = ec2.get_instance_region()
        log.debug('Region not provided using ec2 instance region: %s', region)

    # determine vpc
    env_vpc_id = os.getenv('VPC_ID')
    env_vpc_name = os.getenv('VPC_NAME')
    vpc_id = None
    if env_vpc_name:
        vpc_id = ec2.get_vpc_id_using_vpc_name(env_vpc_name, region)
    if env_vpc_id and not vpc_id:
        log.debug('VPC_ID environment setting: %s', env_vpc_id)
        vpc_id = env_vpc_id
    elif env_vpc_id and env_vpc_id != vpc_id:
        log.error('VPC_ID and VPC_NAME do not match')
        raise Exception('VPC_ID and VPC_NAME specified and not equivalent')
        exit(1)

    # no vpc provided so use ec2 instance
    if not vpc_id:
        vpc_id = ec2.get_instance_vpc_id()
        log.debug(
            'No environment for VPC specified using instance vpc-id: %s',
            vpc_id)

    instances = ec2.get_ec2_instances_in_vpc(vpc_id, region)
    vpc = inv_util.create_inventory([
        inv_util.create_inventory_group(
            'vpc_inventory',
            [v['PrivateIpAddress'] for k, v in instances.iteritems()]
        )]
    )

    if args.list:
        print json.dumps(vpc, indent=2)

    # should not be called by ansible since _meta is in inventory added for
    # backwards compatability for ansible <= 1.3
    if args.host:
        print json.dumps('{}')
