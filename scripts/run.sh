#!/bin/bash
set -e

# Constants
ENDPOINT="http://localhost:9000"
BUCKET="my-bucket"
ZIP_KEY="uploads/test.zip"
RESULT_KEY="results/skull.ply"
LOCAL_ZIP="test.zip"
LOCAL_RESULT="result.ply"

echo "📦 Starting local MinIO..."
docker compose up -d minio

# Give MinIO time to become ready
sleep 5

# Check for test.zip
if [ ! -f "$LOCAL_ZIP" ]; then
  echo "❌ $LOCAL_ZIP not found."
  echo "Please zip your test_images/ folder into test.zip first:"
  echo "    zip -r test.zip test_images/"
  exit 1
fi

# Configure AWS CLI for MinIO
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_EC2_METADATA_DISABLED=true

echo "📤 Uploading test.zip to MinIO..."
aws --endpoint-url "$ENDPOINT" s3 mb "s3://$BUCKET" || true
aws --endpoint-url "$ENDPOINT" s3 cp "$LOCAL_ZIP" "s3://$BUCKET/$ZIP_KEY"

echo "🔧 Building processor container..."
docker compose rm -f processor >/dev/null 2>&1 || true
docker compose build processor

echo "🚀 Running processor job..."
docker compose up --force-recreate processor

echo "📜 Fetching logs..."
docker compose logs -f processor

echo "📥 Downloading result: $RESULT_KEY"
aws --endpoint-url "$ENDPOINT" s3 cp "s3://$BUCKET/$RESULT_KEY" "$LOCAL_RESULT" \
  && echo "✅ Result saved to $LOCAL_RESULT" \
  || echo "⚠️  Result not found — check processor logs."
