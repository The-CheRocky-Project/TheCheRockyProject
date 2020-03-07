import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')

# Get the object from the event and show its content type


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'],
                                    encoding='utf-8')
    try:
        rekognition = boto3.client('rekognition')
        result = rekognition.detect_custom_labels(
            ProjectVersionArn='arn:aws:rekognition:us-east-2:' /
            '693949087897:' /
            'project/redcards/version/redcards.2020-02-28T13.32.38/' /
            '1582893159014',
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            })
        customLabels = result['CustomLabels']
        resNum = len(customLabels)
        if resNum != 0:
            splitted = key.split('/')
            newkey = key[:-len(splitted[len(splitted)-1])]
            oldKey = splitted[len(splitted)-1]
            newkey = newkey + oldKey[:-4]
            newkey = newkey + 'rekoRes.json'
            s3Writer = boto3.resource('s3')
            outStream = s3Writer.Object(bucket, newkey)
            bToWrite = json.dumps(result)
            outStream.put(Body=bToWrite)
        return {
            'bucket': bucket,
            'key': key
        }
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}'.format(key, bucket))
        raise e
