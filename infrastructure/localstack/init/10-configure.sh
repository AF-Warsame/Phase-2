#!/usr/bin/env bash
set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
BUCKET="${REGISTRY_ARTIFACT_BUCKET:-model-registry-artifacts}"
TABLE="${REGISTRY_METADATA_TABLE:-ModelRegistryMetadata}"

echo "[localstack-init] Ensuring S3 bucket ${BUCKET}"
awslocal s3api create-bucket --bucket "${BUCKET}" --region "${REGION}" >/dev/null 2>&1 || true

echo "[localstack-init] Ensuring DynamoDB table ${TABLE}"
if ! awslocal dynamodb describe-table --table-name "${TABLE}" >/dev/null 2>&1; then
  awslocal dynamodb create-table \
    --table-name "${TABLE}" \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions AttributeName=model_id,AttributeType=S \
    --key-schema AttributeName=model_id,KeyType=HASH \
    >/dev/null
fi

echo "[localstack-init] Seeding baseline item for integration tests"
awslocal dynamodb put-item \
  --table-name "${TABLE}" \
  --item '{
    "model_id": {"S": "baseline-seed-model"},
    "artifact_uri": {"S": "s3://'${BUCKET}'/baseline/seed.zip"},
    "status": {"S": "INIT"}
  }' >/dev/null
