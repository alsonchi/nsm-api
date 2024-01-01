import json
import auth
import boto3
import time
import uuid

ws = boto3.client("apigatewaymanagementapi", endpoint_url="https://izur3tdlq9.execute-api.ap-southeast-1.amazonaws.com/poc")
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
userTable = dynamodb.Table("nsm-user")

def sendMsg(receiver, payload):
    try:
        ws.post_to_connection(Data=json.dumps(payload), ConnectionId=receiver)
    except:
        print(receiver + " - Connection is closed")

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
    
    
    # get data
    data = json.loads(event["body"])
    conversationId = data["conversation_id"]
    msgType = data["type"]
    msgBody = data["body"]

    
    #create message record
    msgTable = dynamodb.Table("nsm-message")
    msgTable.put_item(
      Item={
        'uuid': str(uuid.uuid4()),
        'conversation_id': conversationId,
        'sender': user['user_name'],
        'send_at': str(time.time()),
        'type': msgType,
        'body': msgBody,
      } 
    )


    #find conversation
    conversationTable = dynamodb.Table("nsm-conversation")
    conversation = conversationTable.query(
        KeyConditions={
            "uuid": {"AttributeValueList": [conversationId], "ComparisonOperator": "EQ"}
        }
    )

    if len(conversation["Items"]) <= 0: 
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "not_found", "message": "Conversation not found"}),
        }
    
    # notifiy user 
    conversationUsers = conversation["Items"][0]["users"]
    
    receivers = userTable.scan(
        AttributesToGet=[
            'ws_connection_id',
        ],
        Select='SPECIFIC_ATTRIBUTES',
        ScanFilter={
            'user_name': {
                'AttributeValueList': conversationUsers,
                'ComparisonOperator': 'IN'
            }
        }
    )

    for receiver in receivers['Items']:
        if receiver['ws_connection_id'] is not None:
            sendMsg(receiver['ws_connection_id'], {
                'conversationId': conversationId,
                'type': msgType,
                'body': msgBody,
            })

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Send")}
