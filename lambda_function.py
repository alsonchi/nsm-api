import json
import jwt
import boto3

def auth(headers):
    if "Authorization" not in headers:
        return None
        
    token = (headers["Authorization"]).replace("Bearer ", "")
    
    #jwt decode
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    
    #check user token
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
    table = dynamodb.Table("nsm-user")
    
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
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(user)
    }
