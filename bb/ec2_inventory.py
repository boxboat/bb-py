#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import os
import argparse
import json
import logging

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
        'Ansible EC2 Dynamic Inventory - set INVENTORY_DEFINITION in the '
        'environment to point to an inventory definition file (see '
        'documentation) and this script will generate a dynamic '
        'inventory based on the definition .')
    parser = argparse.ArgumentParser(
        description=description)
    parser.add_argument(
        '--list',
        action='store_true',
        help='Print ansible dynamic inventory')
    parser.add_argument('--host')
    parser.add_argument(
        '--debug',
        action='store_true'
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

    def_yaml = os.getenv('INVENTORY_DEFINITION')
    if not def_yaml:
        print 'No INVENTORY_DEFINITION defined in environment!'
        parser.print_help()
        exit(1)

    if args.list:
        print json.dumps(
            inv_util.create_dynamic_ec2_inventory(
                def_yaml,
                region
            ),
            indent=2
        )

    # should not be called by ansible since _meta is in inventory added for
    # backwards compatability for ansible <= 1.3
    if args.host:
        print json.dumps('{}')
