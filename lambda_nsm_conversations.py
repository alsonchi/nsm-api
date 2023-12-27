import auth
import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

def lambda_handler(event, context):

    user = auth.auth(event['headers'])
    
    if user is None:
        return {
            'statusCode': 401,
            'body': json.dumps({"code": "unauthorized", "message": "Unauthorized"}),
        }
    
    conversationTable = dynamodb.Table("nsm-conversation")

    conversations = conversationTable.scan(
        FilterExpression= Attr("users").contains(user['user_name'])
    )

    return {
        'statusCode': 200,
        'body': json.dumps(conversations['Items'])
    }
