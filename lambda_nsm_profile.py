import json
import auth
import boto3

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("nsm-user")

def lambda_handler(event, context):
    user = auth.auth(event['headers'])
    
    if user is None:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "unauthorized", "message": "Unauthorized"}),
        }
    
    resource = {
        'uuid' : user["Items"][0].get('uuid'),
        'user_name': user["Items"][0].get('user_name'),
        'display_name' : user["Items"][0].get('display_name'),
        'avatar' : user["Items"][0].get('avatar'),
        'status': user["Items"][0].get('status'),
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({resource})
    }
    