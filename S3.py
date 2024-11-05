import sys
import argparse
import threading
import os
import logging
import json
import boto3
import requests
import botocore
from botocore.client import Config
from botocore.handlers import set_list_objects_encoding_type_url
from botocore.exceptions import ClientError, NoCredentialsError
from boto3.s3.transfer import TransferConfig
import math

logger = logging.getLogger('app')
hdlr = logging.FileHandler('c:\\Temp\\app.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info('Mercury S3 Utility')


def test_bucket(bucket_name):
    try:
        resp = s3.head_bucket(Bucket=bucket_name)
        logger.info('Bucket %s exist' % (bucket_name))
        logger.info(resp)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error('bucket access %s' % error_code)
        if error_code:
            return False
    return True

def enable_verID(bucket_name):
    try:
        versioning = s3res.BucketVersioning(bucket_name)
        resp = s3.get_bucket_versioning(Bucket=bucket_name)
        if 'Status' in resp and resp['Status'] == 'Suspended':
            # enable versioning
            versioning.enable()
            resp_update = s3.get_bucket_versioning(Bucket=bucket_name)
            logger.info('Bucket Versioning status - %s' % (resp_update['Status']))

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error('bucket access %s' % error_code)
        if error_code:
            return False
    return True

def disable_verID(bucket_name):
    try:
        versioning = s3res.BucketVersioning(bucket_name)
        resp = s3.get_bucket_versioning(Bucket=bucket_name)
        if 'Status' in resp and resp['Status'] == 'Enabled':
            # disable versioning
            versioning.suspend()
            resp_update = s3.get_bucket_versioning(Bucket=bucket_name)
            logger.info('Bucket Versioning status - %s' % (resp_update['Status']))

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error('bucket access %s' % error_code)
        if error_code:
            return False
    return True

def list_s3_keys(bucket, keyprefix):
    paginator = s3.get_paginator('list_objects')
    parameters = {'Bucket': bucket,
                  'Prefix': keyprefix}
    keys = []
    result = dict()
    try:
        resp = paginator.paginate(**parameters)
        logger.info('getting object keys in bucket - %s' % bucket)
        # logger.info(resp.build_full_result())
        l = resp.build_full_result()
        if 'Contents' not in l:
            logger.info(resp)
            return []
        for obj in l['Contents']:
            keys.append(obj['Key'])
            logger.info(obj['Key'])
            # logger.info("get keys completed successful")

        if keys:
            result['keys'] = sorted(keys)

    except ClientError as e:
        logger.error(e)
        raise

    return result

def list_s3_keys_verID(bucket, keyprefix):
    paginator = s3.get_paginator('list_object_versions')
    parameters = {'Bucket': bucket,
                  'Prefix': keyprefix}
    keys = []

    try:

        resp = paginator.paginate(**parameters)
        logger.info('getting object keys in bucket - %s' % bucket)
        # logger.info(resp.build_full_result())
        l = resp.build_full_result()
        if 'Versions' not in l:
            logger.info(resp)
            return []
        for obj in l['Versions']:
            keys.append(obj)
            logger.info(obj)

    except ClientError as e:
        logger.error(e)
        raise

    return keys


def upload(source_file, bucket_name, object_key, contenttype):
    # upload less than 5Gb
    try:
        logger.info('Uploading %s to bucket - %s' % (source_file, bucket_name))
        with open(source_file, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, object_key, ExtraArgs={'ContentType': contenttype},
                              Callback=ProgressPercentage(source_file))

    except ClientError as e:
        logger.error(e)
        raise
    return True


def s3_download_paginate(bucket_name, source_key, target):
    paginator = s3.get_paginator('list_objects')
    parameters = {'Bucket': bucket_name,
                  'Prefix': source_key}
    keys = []
    directory = []

    try:
        resp = paginator.paginate(**parameters)
        list_resp = resp.build_full_result()
        contents = list_resp.get('Contents')
        for obj in contents:
            try:
                i = obj.get('Key')
                if i[-1] != '/':
                    keys.append(i)
                    logger.info('filename %s is queued for download' % i)
                else:
                    directory.append(i)

            except ClientError as e:
                logger.error('An error occurred with %s' % e)

        for dirs in directory:
            logger.info('download target set to %s' % target)
            dest_pathname = os.path.join(target, dirs)
            logger.info(dest_pathname)
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
        for filename in keys:
            logger.info('download target key set to %s' % target)
            filename2 = filename.replace('/', '\\')
            logger.info(filename2)
            dest_pathname = os.path.join(target, filename2)
            logger.info(dest_pathname)
            if not os.path.exists(os.path.dirname(dest_pathname)):
                logger.info('making director %s' % dest_pathname)
                os.makedirs(os.path.dirname(dest_pathname))
            try:
                logger.info('downloading %s from bucket - %s. file will be saved as - %s ' % (
                    filename, bucket_name, dest_pathname))
                s3.download_file(bucket_name, filename, dest_pathname, Callback=DownloadProgressPercentage(filename, (
                    s3.head_object(Bucket=bucket_name, Key=filename))["ContentLength"]))

            except ClientError as e:
                logger.error(e)

    except ClientError as e:
        logger.error(e)
        # raise
    return True


def multi_part_upload_with_s3(source_file, object_key, bucketname, contenttype):
    # Multipart upload files > 5Gb
    config = TransferConfig(multipart_threshold=1024 * 1024 * 5, max_concurrency=10,
                            multipart_chunksize=1024 * 1024, use_threads=True)
    file_path = source_file
    key_path = object_key
    logger.info("%s > 5Gb.... Mulitpart upload will be used" % file_path)
    s3.upload_file(file_path, bucketname, key_path,
                   ExtraArgs={'ContentType': contenttype},
                   Config=config,
                   Callback=ProgressPercentage(file_path))


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)        " % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            logger.info(
                "\r%s  %s / %s  (%.2f%%)        " % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


class DownloadProgressPercentage(object):
    def __init__(self, filename, filesize):
        self._filename = filename
        self._size = filesize
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        def convertSize(size):
            if size == 0:
                return '0B'
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(size, 1024)))
            p = math.pow(1024, i)
            s = round(size / p, 2)
            return '%.2f %s' % (s, size_name[i])

        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)        " % (
                    self._filename, convertSize(self._seen_so_far), convertSize(self._size),
                    percentage))
            logger.info(
                "\r%s  %s / %s  (%.2f%%)        " % (
                    self._filename, convertSize(self._seen_so_far), convertSize(self._size),
                    percentage))

            sys.stdout.flush()


class ArgsToPass(object):

    def __init__(self):
        # args here
        self.action = args.action
        self.key = args.key
        self.path = args.path
        self.bucket = args.bucket
        self.destination = args.destination
        self.contenttype = args.contenttype
        self.accesskey = args.accesskey
        self.secretkey = args.secretkey
        self.endpointuri = args.endpointuri

    def s3client(self):
        ACCESS_KEY = self.accesskey
        SECRET_KEY = self.secretkey
        REGION_NAME = 'na'
        ENDPOINT_URI = self.endpointuri  # 'https://object-uat-na.jpmchase.net:8443'
        version = 's3v4'
        logger.info('Generating Client Access Key and Secret Access Key')
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          region_name=REGION_NAME,
                          endpoint_url=ENDPOINT_URI,
                          verify=True,
                          config=Config(signature_version=version,
                                                        s3={'addressing_style': 'path',
                                                            'payload_signing_enabled': True}))
        s3.meta.events.unregister('before-parameter-build.s3.ListObjects',
            set_list_objects_encoding_type_url)
        
        s3.meta.events.unregister('before-parameter-build.s3.ListObjectVersions' ,
            set_list_objects_encoding_type_url)


        logger.info('Client Access Key and Secret Access Key Generated successful')
        return s3

    def s3res(self):
        ACCESS_KEY = self.accesskey
        SECRET_KEY = self.secretkey
        REGION_NAME = 'na'
        ENDPOINT_URI = self.endpointuri  # 'https://object-uat-na.jpmchase.net:8443'
        version = 's3v4'
        logger.info('Generating Client Access Key and Secret Access Key')
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
            endpoint_url=ENDPOINT_URI,
            config=Config(signature_version=version,
                            s3={'addressing_style': 'path',
                                'payload_signing_enabled': True}))

        logger.info('S3 Resource Access Key and Secret Access Key Generated successful')
        return s3_resource

    def get_s3_action(self):
        if self.action == 'test':
            test_result = test_bucket(self.bucket)
            print(test_result)

        elif self.action == 'enable_VersionID':
            enable_result = enable_verID(self.bucket)
            if enable_result == True:
                logger.info('Enabled Versioning completed successful')

        elif self.action == 'disable_VersionID':
            disable_result = disable_verID(self.bucket)
            if disable_result == True:
                logger.info('Suspended Versioning completed successful')
        elif self.action == 'get':
            get_result = list_s3_keys(self.bucket, self.key)
            print(get_result)
        elif self.action == 'getverID':
            getVerID_result = list_s3_keys_verID(self.bucket, self.key)
            print(getVerID_result)
        elif self.action == 'upload':
            upload_result = upload(self.path, self.bucket, self.key, self.contenttype)
            if upload_result == True:
                logger.info('Upload completed successful')
            print(upload_result)

        elif self.action == 'download':
            download_result = s3_download_paginate(self.bucket, self.key, self.destination)
            if download_result == True:
                logger.info('download completed successful')
            print(download_result)
        elif self.action == 'multipart':
            multipart_result = multi_part_upload_with_s3(self.path, self.key, self.bucket, self.contenttype)
            print(multipart_result)

        else:
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mercury S3 Utility')
    parser.add_argument('--path', metavar='PATH', type=str, help='Enter the Path to file to be uploaded to s3')
    parser.add_argument('--destination', metavar='DESTINATION', type=str,
                        help='Enter the Path to file to be downloaded to local')
    parser.add_argument('--bucket', metavar='BUCKET_NAME', type=str,
                        help='Enter the name of the bucket to which file has to be upload/download/get')
    parser.add_argument('--action', metavar='ACTION',
                        help=' test: test targeted bucket, get: returns list of keys in bucket. upload: write objects to bucket. download: read objects. multipart: upload files > 5Gb',
                        default="get")
    parser.add_argument('--key', metavar='KEY', help='Object key in Mercury')
    parser.add_argument('--contenttype', help='extra argument for object upload')
    parser.add_argument('--accesskey', help='S3 AccessKey')
    parser.add_argument('--secretkey', help='S3 SecretKey')
    parser.add_argument('--endpointuri', help='S3 Endpoint URi')
    parser.add_argument('--versionID', help='Object VersionID')

    args = parser.parse_args()
    shell = ArgsToPass()
    s3 = shell.s3client()
    s3res = shell.s3res()
    shell.get_s3_action()
