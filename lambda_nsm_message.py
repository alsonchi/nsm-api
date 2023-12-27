import auth
import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

def lambda_handler(event, context):
    
    user = auth.auth(event['headers'])
    
    conversationId = event['queryStringParameters']['conversation_id'];
    last = event['queryStringParameters'].get('last')
    
    #check user in conversation
    conversationTable = dynamodb.Table("nsm-conversation")
    
    conversation = conversationTable.query(
        KeyConditions={'uuid': {'AttributeValueList': [conversationId], 'ComparisonOperator': 'EQ'}},
        FilterExpression=Attr("users").contains(user['user_name'])
    )
    
    if conversation['Count'] <= 0:
        return {
            'statusCode': 404,
            'body': json.dumps({"code": "conversation_not_found", "message": "Conversation not found"}),
        }
    
    #get history
    msgTable = dynamodb.Table("nsm-message")
    
    if last is not None:
        message = msgTable.query(
            KeyConditions={
                'conversation_id': {
                    'AttributeValueList': [conversationId],
                    'ComparisonOperator': 'EQ'
                }
            },
            ScanIndexForward=False,
            ExclusiveStartKey={
                "conversation_id": conversationId,
                "send_at": last
            }
        )
    else:
        message = msgTable.query(
            KeyConditions={
                'conversation_id': {
                    'AttributeValueList': [conversationId],
                    'ComparisonOperator': 'EQ'
                }
            },
            ScanIndexForward=False
        )
   
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': message['Items'],
            'last': message.get('LastEvaluatedKey')
        })
    }