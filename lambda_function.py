import json
import jwt
import boto3

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("nsm-user")

def auth(headers):
    if "Authorization" not in headers:
        return None
        
    token = (headers["Authorization"]).replace("Bearer ", "")
    
    #jwt decode
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    
    #find user
    user = table.query(
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
    
    data = json.loads(event["body"])

    if "username" not in data:
        return {
            'statusCode': 403,
            'body': json.dumps({"code": "missing_input", "message": "username is required"}),
        }

    addUserName = data["username"]

    #check system has this user
    addUser = table.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [addUserName], "ComparisonOperator": "EQ"}
        }
    )

    if addUser is None:
        return {
            'statusCode': 403,
            'body': json.dumps({"code": "user_not_found", "message": "User not found"}),
        }
    
    #check has friends field
    if "friends" not in user:
        user["friends"] = []

    #check add user is not friend
    if addUserName in user["friends"]:
        return {
            'statusCode': 403,
            'body': json.dumps({"code": "already_exists", "message": "Friend already exists"}),
        }
    
    user["friends"].append(addUserName)
    
    #add friends
    table.update_item(Key={'user_name':user['user_name']}, AttributeUpdates={'friends': {'Value': user["friends"], 'Action': "PUT"}})
    
    # TODO implement    
    return {
        'statusCode': 200,
        'body': json.dumps(user)
    }
