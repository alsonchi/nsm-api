import boto3
import jwt

def auth(headers):
    if "Authorization" not in headers:
        return None
        
    token = (headers["Authorization"]).replace("Bearer ", "")
    
    #jwt decode
    payload = jwt.decode(token, "secret", algorithm="HS256")
        
    return payload
    
    username = "alson"
    
    #check user token
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
    table = dynamodb.Table("nsm-user")
    
    #find user
    user = table.query(
        KeyConditions={
            "user_name": {"AttributeValueList": [username], "ComparisonOperator": "EQ"}
        }
    )
    
    #check token
    if user["Items"][0]["token"] != token:
        return None
    
    return user["Items"][0]
    