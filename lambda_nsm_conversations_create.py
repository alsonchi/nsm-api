import json
import boto3
import uuid
import auth

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
userTable = dynamodb.Table("nsm-user")

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
    
    #post data
    data = json.loads(event["body"])
    friend = data["friend"]

    #check user is friend
    if friend not in user['friends']:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "friend_not_found", "message": "Not Found"}),
        }
    
    
    #create new conversation
    conversationTable = dynamodb.Table("nsm-conversation")
    uuid = str(uuid.uuid4())
    conversationTable.put_item(
      Item={
        'uuid': uuid,
        'users': [
            user['user_name'],
            friend,
        ]
      } 
    )

    # TODO implement
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({
            'conversation_id': uuid,
        })
    }
