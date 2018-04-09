#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

import os
import logging
import boto3

from bb.aws import client_factory as aws_client_factory
from bb.utils import file_utils as file_util

log = logging.getLogger(__name__)


def download_s3_uri(s3_uri, dest_dir, region=None):
    """Convenience method that takes an s3:// uri and calls the `download`
    method after parsing the s3 uri

    Parameters
    ----------
        s3_uri: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
        dest_dir: `str`
            directory to place the file or files in the case of downloading a
            path key vice file key. If dest_dir does not exist, will attempt to
            create it.
        region: `str`
            aws region (optional)
    """
    bucket, key = __parse_s3_uri(s3_uri)
    return download(bucket, key, dest_dir, region)


def download(bucket, object_key, dest_dir, region=None):
    """Download from S3

    Parameters
    ----------
        bucket: `str`
            s3 bucket to retrieve object_key from
        object_key: `str`
            key for s3 object. If the object key ends in a slash then download
            will download the contents recursively
        dest_dir: `str`
            directory to place the file or files in the case of downloading a
            path key vice file key. If dest_dir does not exist, will attempt to
            create it.
        region: `str`
            aws region (optional)
    """
    s3 = aws_client_factory.get_s3_resource(region)

    if object_key.startswith('/'):
        object_key = object_key[len('/'):]

    if object_key.endswith('/'):
        paginator = s3.meta.client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(
            Bucket=bucket,
            Prefix=object_key,
            PaginationConfig={'PageSize': 50})
        for page in iterator:
            for obj in page['Contents']:
                if not obj['Key'].endswith('/'):
                    final_dest = (
                        dest_dir
                        + os.sep
                        + obj['Key'][len(object_key):])
                    head, tail = os.path.split(final_dest)

                    if not os.path.exists(head):
                        log.debug('Creating destination dir: %s', head)
                        os.makedirs(head)

                    log.info(
                        'Download s3://%s/%s to %s',
                        bucket,
                        obj['Key'],
                        final_dest)
                    s3.meta.client.download_file(
                        bucket,
                        obj['Key'],
                        final_dest)
    else:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        log.info(
            'Download s3://%s/%s to %s',
            bucket,
            object_key,
            dest_dir + os.sep + os.path.basename(object_key))
        s3.meta.client.download_file(
            bucket,
            object_key,
            dest_dir + os.sep + os.path.basename(object_key))


def remote_copy_s3_uri(src, dest, region=None):
    """Convenience method that takes s3:// URI for src and dest and calls
    `remote_copy` after parsing URIs

    Parameters
    ----------
        src: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
        dest: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
        region: `str`
            aws region (optional)
    """
    src_bucket, src_key = __parse_s3_uri(src)
    dest_bucket, dest_key = __parse_s3_uri(dest)
    return remote_copy(src_bucket, src_key, dest_bucket, dest_key, region)


def remote_copy(src_bucket, src_key, dest_bucket, dest_key, region=None):
    """Remote S3 copy

    Parameters
    ----------
        src_bucket: `str`
            s3 src bucket
        src_key: `str`
            s3 src key
        dest_bucket: `str`
            s3 dest bucket
        dest_key: `str`
            s3 dest key
        region: `str`
            aws region (optional)
    """
    s3 = aws_client_factory.get_s3_resource(region)

    if src_key.startswith('/'):
        src_key = src_key[len('/'):]
    if dest_key.startswith('/'):
        dest_key = dest_key[len('/'):]
    if src_key.endswith('/'):
        if not dest_key.endswith('/'):
            dest_key = dest_key + '/'
        paginator = s3.meta.client.get_paginator('list_objects_v2')
        iterator = paginator.paginate(
            Bucket=src_bucket,
            Prefix=src_key,
            PaginationConfig={'PageSize': 50})
        for page in iterator:
            for obj in page['Contents']:
                    final_dest_key = (
                        dest_key
                        +
                        obj['Key'][len(src_key):]
                    )
                    log.info(
                        'Copy s3://%s/%s to s3://%s/%s',
                        src_bucket,
                        obj['Key'],
                        dest_bucket,
                        final_dest_key)
                    s3.meta.client.copy(
                        {
                            'Bucket': src_bucket,
                            'Key': obj['Key']
                        },
                        dest_bucket,
                        final_dest_key)
    else:
        if (dest_key.endswith('/')):
            dest_key = dest_key + os.path.basename(src_key)
        log.info(
            'Copy s3://%s/%s to s3://%s/%s',
            src_bucket,
            src_key,
            dest_bucket,
            dest_key)
        s3.meta.client.copy(
            {
                'Bucket': src_bucket,
                'Key': src_key
            },
            dest_bucket,
            dest_key)


def upload_s3_uri(src, uri, region=None):
    """Convenience method that takes s3:// URI for src and dest and calls
    `remote_copy` after parsing URIs

    Parameters
    ----------
        src: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
        dest: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
        region: `str`
            aws region (optional)
    """

    bucket, key = __parse_s3_uri(uri)
    return upload(src, bucket, key, region)


def upload(src, dest_bucket, dest_key, region=None):
    """Upload to s3

    Parameters
    ----------
        src: `str`
            src file or directory to upload to s3
        bucket: `str`
            destination bucket
        key: `str`
            destination key
        region: `str`
            aws region (optional)
    """
    s3 = aws_client_factory.get_s3_resource(region)
    if dest_key.startswith('/'):
        dest_key = dest_key[len('/'):]
    if os.path.isdir(src):
        src = os.path.normpath(src)
        if dest_key.endswith('/'):
            dest_key = dest_key.rstrip('/')
        files = file_util.get_files_in_directory(src, False)
        for file in files:
            transfer = boto3.s3.transfer.S3Transfer(s3.meta.client)
            path, filename = os.path.split(file)
            final_key = (
                dest_key
                + '/'
                + os.path.basename(src)
                + path[len(src):]
                + '/'
                + filename)
            log.info('Upload %s to s3://%s/%s', file, dest_bucket, final_key)
            transfer.upload_file(file, dest_bucket, final_key)
    elif os.path.isfile(src):
        transfer = boto3.s3.transfer.S3Transfer(s3.meta.client)
        final_key = dest_key
        if dest_key.endswith('/'):
            final_key = dest_key + os.path.basename(src)
        log.info('Upload %s to s3://%s/%s', src, dest_bucket, final_key)
        transfer.upload_file(src, dest_bucket, final_key)
    else:
        raise Exception('Invalid source')


def __parse_s3_uri(uri):
    """Parse s3 uri into bucket and key `tuple`

    Parameters
    ----------
        s3_uri: `str`
            URI for s3 object of the form `s3://<bucket>/some/path`
    Returns
    -------
    bucket, key `tuple`
    """
    if not uri.startswith('s3://'):
        raise Exception('Invalid S3 URI')
    bucket = uri[len('s3://'):].split('/')[0]
    key = uri[len('s3://' + bucket):]
    return bucket, key
