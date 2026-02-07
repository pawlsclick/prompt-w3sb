#!/usr/bin/env bash
# Copy a local file to S3 bucket w3sb-bucket-pod (region eu-north-1) with public read ACL.
# Uses AWS CLI with credentials from ~/.aws (profile default unless AWS_PROFILE is set).
# Sets object ACL so AllUsers (http://acs.amazonaws.com/groups/global/AllUsers) can read.
#
# Usage:
#   ./scripts/copy_to_w3sb_bucket.sh <local_file> [s3_key]
#
# Examples:
#   ./scripts/copy_to_w3sb_bucket.sh ./podcast_output/podcast_0x19.mp3
#   ./scripts/copy_to_w3sb_bucket.sh ./podcast_output/podcast_0x19.mp3 0x19-w3sb.m4a

set -euo pipefail

BUCKET="w3sb-bucket-pod"
REGION="eu-north-1"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <local_file> [s3_key]"
  echo "  local_file  Path to the file to upload"
  echo "  s3_key     Optional object key (default: basename of local_file)"
  exit 1
fi

LOCAL_FILE="$1"
S3_KEY="${2:-$(basename "$LOCAL_FILE")}"

if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "Error: File not found: $LOCAL_FILE"
  exit 1
fi

echo "Copying $LOCAL_FILE -> s3://${BUCKET}/${S3_KEY}"
aws s3 cp "$LOCAL_FILE" "s3://${BUCKET}/${S3_KEY}" --region "$REGION" --acl public-read

# Object ACL is set to public-read (AllUsers can read); URL is directly usable
OBJECT_URL="https://${BUCKET}.s3.${REGION}.amazonaws.com/${S3_KEY}"
echo "Done. URL: $OBJECT_URL"
echo "$OBJECT_URL"
