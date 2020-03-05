import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.resource('s3')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        #get the singular json
        response = s3.Object(bucket, key)
        originRes= response.get()
        origin = json.loads(originRes['Body'].read().decode('utf-8'))
        #calculate the key of the resume json
        splitted = key.split('/')
        newkey = splitted[len(splitted)-1][:-25]
        newkey = newkey + '.json'
        #opens the destination resource
        dest = s3.Object(bucket, newkey)
        destRes={}
        try:
            destRes = dest.get()
        except Exception as e:
            voidcontent={
                'rekognizements' : [
                    ]
            }
            toSerial=json.dumps(voidcontent)
            dest.put(Body=toSerial)
            destRes = dest.get()
        finally:
            destContent = json.loads(destRes['Body'].read().decode('utf-8'))
            rekoToAppend={
                'framename' : key[:-12] + '.jpg',
                'labels' : origin['CustomLabels']
            }
            destContent['rekognizements'].append(rekoToAppend)
            toSerial = json.dumps(destContent)
            dest.put(Body=toSerial)
            return {
                'bucket' : bucket,
                'key' : key
            }
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
