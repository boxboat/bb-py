#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import logging
import argparse
import re
import collections
import bb

from six import iteritems

from bb.aws import ec2_utils as ec2
from bb.aws import asg_utils as asg
from bb.aws import region_utils as region_util


def __parse_arguments():
    description = (
        'EC2 auto tagger will automatically add a number suffix to your EC2 '
        'instance Name Tag. No arguments are required to execute on an '
        'instance that is part of an auto scaling group.'
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--instance-id',
        required=False,
        help='The EC2 instance-id of the instance to tag. If not provided '
             'will attempt to use the instance id of instance this script '
             'is executing on on'
    )
    parser.add_argument(
        '--asg-name',
        required=False,
        help='AutoScalingGroup to query for a group of instances to tag and '
             'index. If ASG name is unknown at execution time then this '
             'will attempt to locate the ASG this instance belongs to. Do '
             'not provide asg-name if basename is provided.'
    )
    parser.add_argument(
        '--basename',
        required=False,
        help='Basename of instance Name tag, if asg-name is not provided and '
             'the instance is not a member of an ASG then basename will be '
             'used as the basis of searching for similarly named instances. '
             'Do not provide basename is asg-name is provided'
    )
    parser.add_argument(
        '--digits',
        default=2,
        help='Maximum number of digits for number portion of tag. e.g. 3 '
             'results in <name>-00X (default 2)'
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
    return parser, parser.parse_args()


def __tag_instances(instance_id, asg_name, basename, digits):
    log = logging.getLogger(__name__)
    instances = {}
    if asg_name:
        ids = asg.get_asg_ec2_instance_ids(asg_name)
        instances = ec2.get_ec2_instance_info(ids)
    elif basename:
        basename = basename + '*'
        instances = ec2.get_ec2_instances(basename)

    tag_map = {}
    used = {}
    if len(instances) > 0:
        for k, v in iteritems(instances):
            if v['State'] != 'terminated':
                tagged = re.search(r'-\d+$', v['Name'])
                tag_map[k] = {
                    'id': k,
                    'name': v['Name'],
                    'tagged': (tagged is not None)}
                if tagged is not None:
                    used[int(tagged.group(0).lstrip('-'))] = v['Name']
    else:
        log.info('Unable to determine a tagging strategy')
        return 0

    size = len(tag_map)
    if asg_name:
        size = max(asg.get_asg_desired_size(asg_name), size)

    avail = []
    for i in range(0, size):
        if i+1 not in used:
            avail.append(i+1)

    log.debug('Found Instances: %s', tag_map)

    if instance_id in tag_map and not tag_map[instance_id]['tagged']:
        ordered_instances = collections.OrderedDict(sorted(tag_map.items()))
        log.debug('Reordered Instances: %s', ordered_instances)
        idx = 0
        for k, i in iteritems(ordered_instances):
            log.debug('Processing instance: %s', i)
            if k == instance_id:
                name = '{0}-{tag:{fill}>{n}}'.format(
                    i['name'],
                    tag=str(avail[idx]),
                    fill=0,
                    n=digits
                )
                log.info('Assigning new name tag: %s to %s', name, k)
                ec2.set_ec2_instance_name(k, name)
            else:
                if not i['tagged']:
                    idx = idx + 1
    else:
        log.info(
            '%s already tagged as %s',
            instance_id,
            tag_map[instance_id]['name']
        )
    return 0


def main():
    parser, args = __parse_arguments()

    if args.debug:
        bb.setup_logging(__name__, logging.DEBUG)
    else:
        bb.setup_logging(__name__)

    log = logging.getLogger(__name__)

    if args.region:
        region_util.set_region(args.region)

    if args.asg_name and args.basename:
        parser.error('Cannot define basename and asg-name')

    instance_id = args.instance_id
    if not instance_id:
        instance_id = ec2.get_instance_id()
        log.info(
            'Instance id not provided using ec2 instance id: %s',
            instance_id
        )

    asg_name = args.asg_name
    if not asg_name:
        asg_name = asg.get_asg_name(instance_id)
        log.info('Instance is associated with asg named: %s', asg_name)

    return __tag_instances(
        instance_id,
        asg_name,
        args.basename,
        args.digits)
