import json
import auth

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
    
    resource = {
        'uuid' : user.get('uuid'),
        'user_name': user.get('user_name'),
        'display_name' : user.get('display_name'),
        'avatar' : user.get('avatar'),
        'status': user.get('status'),
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(resource)
    }
    