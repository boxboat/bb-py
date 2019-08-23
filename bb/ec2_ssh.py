#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import argparse
import logging
import os
import inquirer

from six import iteritems

import bb
from bb.aws import ec2_utils as ec2
from bb.aws import region_utils as region_util


def __parse_arguments():
    description = (
        'EC2 ssh command')
    parser = argparse.ArgumentParser(
        description=description)
    parser.add_argument(
        'search',
        nargs='?',
        help='Search string for ssh connection')
    parser.add_argument(
        '--user',
        required=False,
        help='Optional user argument to override current user for ssh command'
    )
    parser.add_argument(
        '--public',
        action='store_true',
        help='Use public IP address if available default is to use private IP'
    )
    parser.add_argument(
        '--debug',
        action='store_true'
    )
    parser.add_argument(
        '--region',
        required=False,
        help='AWS Region (default ec2 instance configuration) or it will use '
             'the region this script is executing on'
    )
    return parser, parser.parse_args()


def main():
    parser, args = __parse_arguments()

    if args.debug:
        bb.setup_logging(__name__, logging.DEBUG)
    else:
        bb.setup_logging(__name__, logging.INFO)

    log = logging.getLogger(__name__)

    if args.region:
        region_util.set_region(args.region)

    instances = ec2.get_ec2_instances('*' + args.search + '*')

    selections = []
    for k, v in iteritems(instances):
        if args.public and v.get('PublicIpAddress') is not None:
            selections.append(
                ('{name:{fill}<{n}}{0}'.format(
                    v['PublicIpAddress'],
                    name=v['Name'] + ':',
                    fill=' ',
                    n=30), v['PublicIpAddress']))
        else:
            if v.get('PrivateIpAddress') is not None:
                selections.append(
                    ('{name:{fill}<{n}}{0}'.format(
                        v['PrivateIpAddress'],
                        name=v['Name'] + ':',
                        fill=' ',
                        n=30), v['PrivateIpAddress']))

    log.debug('Selections: %s', sorted(selections))
    selections.append(('Exit', 'exit'))

    question = inquirer.List(
        'ec2-ssh',
        message='SSH to Host',
        choices=selections)

    answer = inquirer.prompt([question])
    host = ''
    if not answer or answer['ec2-ssh'] == 'exit':
        log.info('Exiting')
        return 0

    if args.user:
        host = args.user + '@' + answer['ec2-ssh']
    else:
        host = answer['ec2-ssh']
    log.info('ssh -A %s', host)
    os.execlp("ssh", "ssh", "-A", host)
