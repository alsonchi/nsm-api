import json
import boto3
import jwt
import time

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("nsm-user")

def lambda_handler(event, context):
    data = json.loads(event["body"])

    username = data["user_name"]
    password = data["password"]

    user = table.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [username], "ComparisonOperator": "EQ"}
        }
    )

    if user["Items"][0]["password"] != password:
        return {
            "statusCode": 401,
            "body": json.dumps({"code": "password_incorrect", "message": "Password incorrect"}),
        }
        
    resource = {
        'uuid': user["Items"][0]["uuid"],
        'user_name': user["Items"][0]["user_name"],
        'display_name': user["Items"][0]["display_name"],
        'timestamp': time.time()
    }
    
    token = jwt.encode(resource, "secret", algorithm="HS256")
    
    #update user token
    table.update_item(Key={'user_name':username}, AttributeUpdates={'token': {'Value': token, 'Action': "PUT"}})

    return {"statusCode": 200, "body": json.dumps({
        'user': resource,
        'token': jwt.encode(resource, "secret", algorithm="HS256"),
    })}