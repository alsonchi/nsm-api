import jwt
import boto3

def auth(headers):
    if "Authorization" not in headers:
        return None
        
    token = (headers["Authorization"]).replace("Bearer ", "")
    
    #jwt decode
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
    
    #find user
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
    userTable = dynamodb.Table("nsm-user")
    user = userTable.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [payload['user_name']], "ComparisonOperator": "EQ"}
        }
    )
    
    #check token
    if user["Items"][0]["token"] != token:
        return None
    
    return user["Items"][0]