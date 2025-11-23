# permission - AmazonDynamoDBFullAccess

import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.client("dynamodb")

def lambda_handler(event, context):

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps("OK")
        }

    # Normal POST request
    body = json.loads(event.get("body", "{}"))

    order_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    item = {
        "OrderId": {"S": order_id},
        "timestamp": {"S": timestamp},
        "orderSignature": {"S": body.get("orderSignature", "")},
        "items": {"S": json.dumps(body.get("items", {}))},
        "agent": {"S": body.get("agent", "unknown")}
    }

    dynamodb.put_item(
        TableName="Orders",
        Item=item
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps({
            "message": "Order Saved",
            "orderId": order_id
        })
    }
