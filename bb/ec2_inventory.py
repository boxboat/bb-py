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


def __parse_arguments():
    description = (
        'Ansible EC2 Dynamic Inventory - set INVENTORY_DEFINITION in the '
        'environment to point to an inventory definition file (see '
        'documentation) or yaml string and this script will generate a dynamic '
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
    return parser, parser.parse_args()


def main():
    parser, args = __parse_arguments()

    if args.debug:
        # only establish logging handlers for DEBUG output
        bb.setup_logging(__name__, logging.DEBUG)

    log = logging.getLogger(__name__)

    def_yaml = os.getenv('INVENTORY_DEFINITION')
    if not def_yaml:
        log.error('No INVENTORY_DEFINITION defined in environment!')
        parser.print_help()
        exit(1)

    if args.list:
        print(
            json.dumps(
                inv_util.create_dynamic_ec2_inventory(
                    def_yaml
                ),
                indent=2
            )
        )

    # should not be called by ansible since _meta is in inventory added for
    # backwards compatability for ansible <= 1.3
    if args.host:
        print(json.dumps('{}'))
