import json
import boto3
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
    
    data = json.loads(event["body"])

    if "username" not in data:
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "missing_input", "message": "username is required"}),
        }

    addUserName = data["username"]

    #check user exits
    checkUserResult = userTable.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [addUserName], "ComparisonOperator": "EQ"}
        }
    )

    if len(checkUserResult["Items"]) <= 0:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "user_not_found", "message": "User not found"}),
        }
    
    #check has friends field
    if "friends" not in user:
        user["friends"] = []

    #check add user is not friend
    if addUserName in user["friends"]:
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({"code": "already_exists", "message": "Friend already exists"}),
        }
    
    user["friends"].append(addUserName)
    
    #add friends
    userTable.update_item(Key={'user_name':user['user_name']}, AttributeUpdates={'friends': {'Value': user["friends"], 'Action': "PUT"}})
    
    # TODO implement    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(user)
    }
