#!/bin/bash

set -euo pipefail

PROFILE="tut"
REGION="us-east-1"

# Get all bucket names that start with "cdk-"
buckets=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, 'cdk-')].Name" --output text --profile "$PROFILE" --region "$REGION")

for bucket in $buckets; do
    echo "Processing bucket: $bucket"

    # Suspend versioning
    echo "  Suspending versioning..."
    aws s3api put-bucket-versioning \
        --bucket "$bucket" \
        --versioning-configuration Status=Suspended \
        --profile "$PROFILE" \
        --region "$REGION"

    # Get all object versions
    echo "  Deleting all object versions and delete markers..."
    versions=$(aws s3api list-object-versions --bucket "$bucket" --profile "$PROFILE" --region "$REGION")

    # Delete all versions
    echo "$versions" | jq -c '.Versions[]?' | while read -r version; do
        key=$(echo "$version" | jq -r '.Key')
        versionId=$(echo "$version" | jq -r '.VersionId')
        aws s3api delete-object \
            --bucket "$bucket" \
            --key "$key" \
            --version-id "$versionId" \
            --profile "$PROFILE" \
            --region "$REGION"
    done

    # Delete all delete markers
    echo "$versions" | jq -c '.DeleteMarkers[]?' | while read -r marker; do
        key=$(echo "$marker" | jq -r '.Key')
        versionId=$(echo "$marker" | jq -r '.VersionId')
        aws s3api delete-object \
            --bucket "$bucket" \
            --key "$key" \
            --version-id "$versionId" \
            --profile "$PROFILE" \
            --region "$REGION"
    done

    # Delete the bucket
    echo "  Deleting bucket..."
    aws s3api delete-bucket --bucket "$bucket" --profile "$PROFILE" --region "$REGION"

    echo "  Successfully deleted bucket: $bucket"
done

echo "All cdk-* buckets have been processed."
