# AmazonDynamoDBReadOnlyAccess        --- permission


import json
import boto3

dynamodb = boto3.client("dynamodb")

def lambda_handler(event, context):

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET"
            },
            "body": json.dumps("OK")
        }

    # Scan Whole Table
    response = dynamodb.scan(
        TableName="Orders"
    )

    items = []
    for i in response.get("Items", []):
        items.append({
            "orderId": i["OrderId"]["S"],
            "timestamp": i["timestamp"]["S"],
            "orderSignature": i["orderSignature"]["S"],
            "items": json.loads(i["items"]["S"]),
            "agent": i["agent"]["S"]
        })

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(items)
    }
