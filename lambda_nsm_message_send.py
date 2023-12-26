import json
import jwt
import boto3
import time
import uuid

ws = boto3.client("apigatewaymanagementapi", endpoint_url="https://izur3tdlq9.execute-api.ap-southeast-1.amazonaws.com/poc")
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
userTable = dynamodb.Table("nsm-user")

def auth(headers):
    if "Authorization" not in headers:
        return None
        
    token = (headers["Authorization"]).replace("Bearer ", "")
    
    #jwt decode
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    
    #find user
    user = userTable.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [payload['user_name']], "ComparisonOperator": "EQ"}
        }
    )
    
    #check token
    if user["Items"][0]["token"] != token:
        return None
    
    return user["Items"][0]


def sendMsg(receiver, payload):
    ws.post_to_connection(Data=json.dumps(payload), ConnectionId=receiver['ws_connection_id'])

def lambda_handler(event, context):
        
    user = auth(event['headers'])
    
    if user is None:
        return {
            'statusCode': 401,
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
        'sender': user['username'],
        'send_at': time.time(),
        'type': msgType,
        'body': msgBody,
      } 
    )


    # scan 
    friends = user['friends']
    
    receivers = userTable.scan(
        AttributesToGet=[
            'ws_connection_id',
        ],
        Select='SPECIFIC_ATTRIBUTES',
        ScanFilter={
            'user_name': {
                'AttributeValueList': friends,
                'ComparisonOperator': 'IN'
            }
        }
    )

    for receiver in receivers:
        sendMsg(receiver, {
            'conversationId': conversationId,
            'type': msgType,
            'body': msgBody,
        })

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Send")}
