#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import argparse
import logging

import bb
from bb.aws import s3_utils as s3
from bb.aws import region_utils as aws_region


def __parse_arguments():
    description = (
        'S3 copy command'
    )
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'src',
        nargs='?',
        help='src file/directory s3 or local'
    )
    parser.add_argument(
        'dest',
        nargs='?',
        help='dest file/directory s3 or local'
    )
    parser.add_argument(
        '--region',
        required=False,
        help='AWS Region (default ec2 instance configuration) or it will use '
             'the region this script is executing on'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Turn on debug logging')
    return parser.parse_args()


def main():
    args = __parse_arguments()

    if args.debug:
        bb.setup_logging(__name__, logging.DEBUG)
    else:
        bb.setup_logging(__name__, logging.INFO)
    log = logging.getLogger(__name__)

    region = args.region
    if region:
        aws_region.set_region(region)

    src = args.src
    dest = args.dest

    if src.startswith('s3://') and dest.startswith('s3://'):
        log.debug('Remote copy: [%s] to [%s]', src, dest)
        s3.remote_copy_s3_uri(src, dest)
    elif src.startswith('s3://'):
        log.debug('Download: [%s] to [%s]', src, dest)
        s3.download_s3_uri(src, dest)
    else:
        log.debug('Upload: [%s] to [%s]', src, dest)
        s3.upload_s3_uri(src, dest)
