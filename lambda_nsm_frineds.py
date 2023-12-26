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


def get_user_info(username):

    user = table.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [username], "ComparisonOperator": "EQ"}
        }
    )
    
    if len(user["Items"]) <= 0: 
        return None
    
    return {
        'uuid' : user["Items"][0].get('uuid'),
        'user_name': user["Items"][0].get('user_name'),
        'display_name' : user["Items"][0].get('display_name'),
        'avatar' : user["Items"][0].get('avatar'),
        'status': user["Items"][0].get('status'),
    }
    

def lambda_handler(event, context):
    
    user = auth(event['headers'])
    
    if user is None:
        return {
            'statusCode': 401,
            'body': json.dumps({"code": "unauthorized", "message": "Unauthorized"}),
        }
    
    # get friends info list
    friends = []

    for friend in user["friends"]:
        friend_data = get_user_info(friend)
        if friend_data != None:
            friends.append(friend_data)


    #get user friends list
    return {
        'statusCode': 200,
        'body': json.dumps(friends)
    }
