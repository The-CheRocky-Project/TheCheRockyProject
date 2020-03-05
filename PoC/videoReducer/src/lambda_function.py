import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        mediaConv=boto3.client('mediaconvert', endpoint_url='https://fkuulejsc.mediaconvert.us-east-2.amazonaws.com')
        #mediaConv.describe_endpoints(MaxResults=123, Mode='DEFAULT')
        result=mediaConv.create_job(
            JobTemplate = 'videoFramer',
            Role= 'arn:aws:iam::693949087897:role/lambdaFramer',
            Queue= 'arn:aws:mediaconvert:us-east-2:693949087897:queues/Default',
            Settings= {
                'Inputs': [
                    {
                        'AudioSelectors': {
                            'Audio Selector 1': {
                                'Offset': 0,
                                'DefaultSelection': 'DEFAULT',
                                'ProgramSelection': 1
                            }
                        },
                        'VideoSelector': {
                            'ColorSpace': 'FOLLOW',
                            'Rotate': 'DEGREE_0',
                            'AlphaBehavior': 'DISCARD'
                        },
                        'FilterEnable': 'AUTO',
                        'PsiControl': 'USE_PSI',
                        'FilterStrength': 0,
                        'DeblockFilter': 'DISABLED',
                        'DenoiseFilter': 'DISABLED',
                        'TimecodeSource': 'EMBEDDED',
                        'FileInput': 's3://'+bucket + '/' + key
                    }
                ],
                'OutputGroups': [
                    {
                        'Name': 'File Group',
                        'Outputs': [
                            {
                                'Preset': 'Low',
                                'Extension': 'mp4',
                                'NameModifier': 'low'
                            },
                            {
                                'Preset': 'Framer',
                                'Extension': 'jpg',
                                'NameModifier': 'frame'
                            }
                        ],
                        'OutputGroupSettings': {
                        'Type': 'FILE_GROUP_SETTINGS',
                        'FileGroupSettings': {
                            'Destination': 's3://'+ bucket +'/outConvert/'
                            }
                        }
                    }
                ],
                'AdAvailOffset': 0,
            },
            AccelerationSettings= {
                'Mode': 'DISABLED'
            },
            StatusUpdateInterval= 'SECONDS_60',
            Priority= 0
        )
        return(result['Job']['Id'])
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
