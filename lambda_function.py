import json
import auth

def lambda_handler(event, context):
    
    user = auth.auth(event['headers']);
    
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
