import boto3
import os
from PIL import Image
import io

s3 = boto3.client('s3')
sizes = [128, 256, 512]

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    image_object = s3.get_object(Bucket=source_bucket, Key=object_key)
    image_content = image_object['Body'].read()

    image = Image.open(io.BytesIO(image_content))

    for size in sizes:
        img_copy = image.copy()
        img_copy.thumbnail((size, size))

        buffer = io.BytesIO()
        img_copy.save(buffer, 'JPEG')
        buffer.seek(0)

        dest_bucket = 'resized-image-bucket-yogita'
        resized_key = f"{size}/{object_key}"
        s3.put_object(Bucket=dest_bucket, Key=resized_key, Body=buffer, ContentType='image/jpeg')
        print(f"Uploaded resized image {resized_key}")

    return {"status": "success"}