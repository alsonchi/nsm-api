import json
import jwt
import boto3
import uuid

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

def lambda_handler(event, context):

    user = auth(event['headers'])
    
    if user is None:
        return {
            'statusCode': 401,
            'body': json.dumps({"code": "unauthorized", "message": "Unauthorized"}),
        }
    
    #post data
    data = json.loads(event["body"])
    friend = data["friend"]

    #check user is friend
    if friend not in user['friends']:
        return {
            'statusCode': 404,
            'body': json.dumps({"code": "friend_not_found", "message": "Not Found"}),
        }
    
    
    #create new conversation
    msgTable = dynamodb.Table("nsm-message")
    msgTable.put_item(
      Item={
        'uuid': str(uuid.uuid4()),
        'users': [
            user['username'],
            friend,
        ]
      } 
    )

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('New Conversations Created')
    }
