import json
import boto3
import time
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AbnormalInfoCodes')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    code_id = body.get('code_id')
    description = body.get('description', 'No details')
    timestamp = int(time.time())

    table.put_item(Item={
        'code_id': code_id,
        'timestamp': timestamp,
        'description': description
    })

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Code stored successfully'})
    }
