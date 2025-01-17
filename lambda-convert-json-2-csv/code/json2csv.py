import boto3
import sys
import logging
import os
import subprocess
import json
from libjson2csv import json_2_csv


client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

lambda_tmp_dir = '/tmp'
s3_csv_dir = 'csv'


def lambda_handler(event, context):
    for r in event['Records']:
        s3 = r['s3']
        bucket = s3['bucket']['name']
        key = s3['object']['key']

        # Needed when a delete event on a csv file
        if '.csv' in key:
            logger.debug("found .csv in key {0}".format(key))
            key = key.replace('csv', 'json')

        source = download_json(bucket, key)
        output = os.path.splitext(source)[0] + '.csv'
        convert_json_2_csv(source, output)
        upload_csv(output, bucket)

    logger.info("{0} records processed.".format(len(event['Records'])))
    return True




def download_json(bucket, key):
    local_source_json = lambda_tmp_dir + "/" + key
    directory = os.path.dirname(local_source_json)
    if not os.path.exists(directory):
        os.makedirs(directory)

    client.download_file(bucket, key, local_source_json)
    output = subprocess.check_output(["file", local_source_json])
    logger.debug("json file downloaded to {}".format(str(output, "utf-8")))
    return local_source_json


def convert_json_2_csv(input_file, output_file):
    logger.debug('Start convert_json_2_csv')
    csv_file = open(output_file, 'w')

    try:
        json_data = json.load(open(input_file))
    except IOError as e:
        errno, strerror = e.args
        logger.error("I/O error({0}): {1}".format(errno, strerror))
        raise
    except ValueError:
        logger.error("Error: {0} is not a valid json file".format(input_file))
        logger.error(sys.exc_info()[0])
        raise
    except:
        logger.error("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        json_2_csv.convert_to_csv(json_data, csv_file)
        csv_file.close()
        logger.debug("Finished convert_json_2_csv for {0}".format(input_file))


def upload_csv(local_csv_file, bucket):
    basename = os.path.basename(local_csv_file)
    full_key = "{0}/{1}".format(s3_csv_dir, basename)
    logger.debug('uploading to S3 bucket: {}, key: {}'.format(bucket, full_key))
    client.upload_file(local_csv_file, bucket, full_key)
