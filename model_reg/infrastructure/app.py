# Re-export the comprehensive handlers from src/api
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from api.handlers import lambda_handler
except ImportError:
    # Fallback to basic implementation if src not available
    import boto3
    import uuid
    import json
    import logging
    from datetime import datetime
    from botocore.exceptions import ClientError

    # Initialize AWS clients
    s3_client = boto3.client("s3")
    dynamodb_client = boto3.resource("dynamodb")
    table = dynamodb_client.Table(os.getenv("DYNAMODB_TABLE_NAME"))

    # Configure structured JSON logging
    logging.basicConfig(format=json.dumps({"timestamp": "%(asctime)s", "message": "%(message)s"}))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    def lambda_handler(event, context):
        """Basic API Gateway dispatcher for the Lambda function."""
        try:
            # Generate a correlation ID for request tracing
            correlation_id = str(uuid.uuid4())
            logger.info(f"Handling request with Correlation ID: {correlation_id}")

            # Dispatch based on HTTP method
            method = event["httpMethod"]
            path = event["path"]

            if path == "/models":
                if method == "GET":
                    return list_models(correlation_id)
                elif method == "POST":
                    return upload_model(event, correlation_id)
                elif method == "DELETE":
                    return delete_model(event, correlation_id)

            elif path == "/health":
                return health_check()

            return {"statusCode": 404, "body": json.dumps({"error": "Not Found"})}

        except Exception as e:
            logger.error({"error": str(e)})
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Internal Server Error"})
            }


def upload_model(event, correlation_id):
    """Handle model upload to S3 and metadata storage in DynamoDB."""
    body = json.loads(event["body"])
    model_id = body.get("model_id")
    metadata = body.get("metadata", {})
    model_data = body.get("data")

    if not model_id or not model_data:
        logger.warning(f"CorrelationID {correlation_id}: Invalid request payload.")
        return {"statusCode": 400, "body": json.dumps({"error": "Missing model_id or data"})}

    try:
        # Upload the model to S3
        s3_client.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=f"models/{model_id}",
            Body=model_data.encode("utf-8")
        )

        # Store metadata in DynamoDB
        table.put_item(
            Item={
                "model_id": model_id,
                "metadata": metadata,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )

        logger.info(f"CorrelationID {correlation_id}: Successfully uploaded model {model_id}")
        return {"statusCode": 201, "body": json.dumps({"message": "Model uploaded successfully"})}

    except ClientError as error:
        logger.error(f"CorrelationID {correlation_id}: {error.response['Error']}")
        return {"statusCode": 500, "body": json.dumps({"error": "Upload failed"})}


def list_models(correlation_id):
    """List models with metadata from DynamoDB."""
    try:
        response = table.scan()
        logger.info(f"CorrelationID {correlation_id}: Retrieved {len(response.get('Items', []))} models.")
        return {"statusCode": 200, "body": json.dumps(response.get("Items", []))}

    except ClientError as error:
        logger.error(f"CorrelationID {correlation_id}: {error.response['Error']}")
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to list models"})}


def delete_model(event, correlation_id):
    """Delete model from S3 and DynamoDB."""
    model_id = event["queryStringParameters"].get("model_id")
    if not model_id:
        logger.warning(f"CorrelationID {correlation_id}: Missing model_id in request.")
        return {"statusCode": 400, "body": json.dumps({"error": "model_id is required"})}

    try:
        # Delete from S3
        s3_client.delete_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=f"models/{model_id}"
        )

        # Delete from DynamoDB
        table.delete_item(Key={"model_id": model_id})

        logger.info(f"CorrelationID {correlation_id}: Successfully deleted model {model_id}.")
        return {"statusCode": 204, "body": ""}

    except ClientError as error:
        logger.error(f"CorrelationID {correlation_id}: {error.response['Error']}")
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to delete model"})}


def health_check():
    """Return system health status and metrics."""
    return {"statusCode": 200, "body": json.dumps({"status": "healthy", "time": datetime.utcnow().isoformat()})}