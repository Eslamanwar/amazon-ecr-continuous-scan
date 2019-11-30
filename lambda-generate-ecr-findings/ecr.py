import boto3
import json
import datetime
from dateutil.tz import tzutc
import csv
import sys

def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.timestamp()
        
        
def lambda_handler(event, context):
    client1 = boto3.client('ecr')
    response = client1.describe_image_scan_findings(
    registryId='215745394840',
    repositoryName='amazonlinux',
    imageId={
        'imageTag': 'latest'
    },
    maxResults=123
    )

    response_json = json.dumps(response , default=convert_timestamp)

    s3 = boto3.resource('s3')
    object1 = s3.Object('ecr-continuous-scan-json-csv', 'json/findings-test3.json')
    object1.put(Body=response_json)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

