#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import argparse
import logging

import bb
from bb.aws import ec2_utils as ec2
from bb.aws import route53_utils as route53
from bb.aws import region_utils as region_util


def __parse_arguments():
    description = (
        'Route53 EC2 instance DNS command. Updates private or public hosted '
        'zones using either the provided name and ip address(es) or will '
        'automatically use the Name and Resource tag to generate a DNS record. '
        'Automatic generation will remove the Resource tag prefix if it is '
        'defined from the beginning of the Name tag. e.g. Resource: foo, Name: '
        'foo-bar-02, Public Zone: foo.com will result in bar-02.foo.com')

    parser = argparse.ArgumentParser(
        description=description)
    parser.add_argument(
        '--private-zone',
        required=False,
        help='Route53 private hosted zone name (must provide private or public)'
    )
    parser.add_argument(
        '--public-zone',
        required=False,
        help='Route53 public hosted zone name (must provide private or public)'
    )
    parser.add_argument(
        '--private-zone-id',
        required=False,
        help='Route53 private hosted zone ID only required if you have '
             'duplicate zone names'
    )
    parser.add_argument(
        '--public-zone-id',
        required=False,
        help='Route53 public hosted zone ID only required if you have '
             'duplicate zone names'
    )
    parser.add_argument(
        '--private-ip',
        required=False,
        help='Optional EC2 private ip address'
    )
    parser.add_argument(
        '--public-ip',
        required=False,
        help='Optional EC2 public ip address'
    )
    parser.add_argument(
        '--name',
        required=False,
        help='Optional EC2 name to prefix to zones'
    )

    parser.add_argument(
        '--public-zone-prefix',
        required=False,
        help='Optional public zone prefix i.e. result of command will be '
             '<name>.<prefix>.<public-zone>'
    )

    parser.add_argument(
        '--private-zone-prefix',
        required=False,
        help='Optional private zone prefix i.e. result of command will be '
             '<name>.<prefix>.<private-zone>'
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


def __update_record(name, zone_prefix, zone, zone_id, ip_address):
    return route53.create_or_update_dns_a_record(
        name,
        zone_prefix,
        zone,
        ip_address,
        zone_id)


def main():
    parser, args = __parse_arguments()

    if args.debug:
        bb.setup_logging(__name__, logging.DEBUG)
    else:
        bb.setup_logging(__name__, logging.INFO)

    log = logging.getLogger(__name__)

    if args.region:
        region_util.set_region(args.region)

    name = None
    if args.name is not None:
        name = args.name
        log.info('Using provided name: %s', name)
    else:
        name = ec2.get_current_instance_name(strip_resource_tag=True)
        log.info('Using current ec2 instance name: %s', name)

    private_ip = None
    if args.private_ip is not None:
        private_ip = args.private_ip
        log.info('Using provided private ip: %s', private_ip)
    else:
        private_ip = ec2.get_current_instance_private_ip()
        log.info('Using current ec2 private ip: %s', private_ip)

    public_ip = None
    if args.public_ip is not None:
        public_ip = args.public_ip
        log.info('Using provided public ip: %s', public_ip)
    else:
        public_ip = ec2.get_current_instance_public_ip()
        log.info('Using current ec2 public ip: %s', public_ip)

    if args.private_zone and private_ip:
        __update_record(name,
                        args.private_zone_prefix,
                        args.private_zone,
                        args.private_zone_id,
                        private_ip)

    if args.public_zone and public_ip:
        __update_record(name,
                        args.public_zone_prefix,
                        args.public_zone,
                        args.public_zone_id,
                        public_ip)
