import boto3
import re
import os

s3 = boto3.client("s3")

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', re.IGNORECASE)
PASSWORD_RE = re.compile(r'\bpassword\b\s*[:=]\s*["\']?([^\s"\'`]+)', re.IGNORECASE)
SECRET_RE = re.compile(r'\bsecret\b\s*[:=]\s*["\']?([^\s"\'`]+)', re.IGNORECASE)
AWS_KEY_RE = re.compile(r'AKIA[0-9A-Z]{16}')
GENERIC_KEY_RE = re.compile(r'\b(?:api[_-]?key|apikey|token)\b\s*[:=]\s*["\']?([A-Za-z0-9\-\._]{10,})', re.IGNORECASE)

def redact(value):
    if not value:
        return "REDACTED"
    v = str(value)
    if len(v) <= 6:
        return "REDACTED"
    return v[:3] + "..." + v[-2:]

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    local_path = f"/tmp/{os.path.basename(key)}"
    s3.download_file(bucket, key, local_path)

    with open(local_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    findings = []

    emails = EMAIL_RE.findall(content)
    if emails:
        findings.append({"type": "email", "count": len(emails), "examples": list(set(emails))[:3]})

    passwords = PASSWORD_RE.findall(content)
    if passwords:
        findings.append({
            "type": "password",
            "count": len(passwords),
            "examples": [redact(p) for p in passwords[:3]]
        })

    secrets = SECRET_RE.findall(content)
    if secrets:
        findings.append({
            "type": "secret",
            "count": len(secrets),
            "examples": [redact(s) for s in secrets[:3]]
        })

    aws_keys = AWS_KEY_RE.findall(content)
    if aws_keys:
        findings.append({"type": "aws_key", "count": len(aws_keys), "examples": [redact(k) for k in aws_keys[:3]]})

    gen_keys = GENERIC_KEY_RE.findall(content)
    if gen_keys:
        findings.append({"type": "api_key_like", "count": len(gen_keys), "examples": [redact(k) for k in gen_keys[:3]]})

    if findings:
        print(f"⚠️ Sensitive info found in {key}: {findings}")
    else:
        print(f"✅ No sensitive info found in {key}")

    return {"statusCode": 200, "file": key, "findings": findings}
