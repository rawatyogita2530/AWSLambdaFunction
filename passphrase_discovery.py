import boto3
import json
import string
import datetime
import re  # ✅ Added for extracting numeric index

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Table references
dict_table = dynamodb.Table('Dictionary')
checks_table = dynamodb.Table('Checks')
matches_table = dynamodb.Table('Matches')


# 🧠 Function: Atbash Cipher (A↔Z, B↔Y, etc.)
def atbash_cipher(text):
    alphabet = string.ascii_lowercase
    reversed_alpha = alphabet[::-1]
    table = str.maketrans(alphabet, reversed_alpha)
    return text.translate(table)


# 🧩 Main Lambda Handler
def lambda_handler(event, context):
    try:
        # Loop through each record in the event
        for record in event.get('Records', []):
            msg = json.loads(record['body'])
            s3_info = msg['Records'][0]['s3']
            bucket = s3_info['bucket']['name'].strip()  # remove extra spaces
            key = s3_info['object']['key']

            print(f"📂 Processing file: {key} from bucket: {bucket}")

            # ✅ Extract numeric file index (e.g., "frp/frp-5000.txt" -> 5000)
            match = re.search(r'(\d+)', key)
            file_index_num = int(match.group(1)) if match else 0

            # Get file content
            obj = s3.get_object(Bucket=bucket, Key=key)
            data = obj['Body'].read().decode('utf-8').strip()

            # Step 1️⃣: Discard first 2 and last 2 characters
            if len(data) <= 4:
                print("⚠️ Invalid data length, skipping file.")
                continue
            data = data[2:-2]

            # Step 2️⃣: Reverse the string
            data = data[::-1]

            # Step 3️⃣: Convert to lowercase
            data = data.lower()

            # Step 4️⃣: Apply Atbash cipher
            decoded = atbash_cipher(data)
            print(f"🔐 Decoded text: {decoded}")

            # Step 5️⃣: Check Dictionary table
            resp = dict_table.get_item(Key={'passphrase': decoded})
            now = datetime.datetime.utcnow().isoformat()

            if 'Item' in resp:
                # ✅ Match found — save to Matches table
                matches_table.put_item(Item={
                    'timestamp': now,
                    'fileIndex': file_index_num,   # ✅ Number type now
                    'passphrase': decoded
                })
                print(f"✅ Match found: {decoded} for {file_index_num}")
            else:
                # ❌ No match — save to Checks table
                checks_table.put_item(Item={
                    'timestamp': now,
                    'fileIndex': file_index_num,   # ✅ Number type now
                    'passphrase': decoded
                })
                print(f"❌ No match: {decoded} for {file_index_num}")

        return {'statusCode': 200, 'body': 'Processing complete.'}

    except Exception as e:
        print(f"❗ ERROR: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}