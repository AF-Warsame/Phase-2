# infrastructure/model_registry/model_registry_stack.py
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class ModelRegistryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------
        # S3 Bucket for model storage
        # ------------------------
        self.model_bucket = s3.Bucket(
            self, "ModelStorage",
            removal_policy=RemovalPolicy.RETAIN,
            versioned=True
        )

        # ------------------------
        # DynamoDB Table for metadata
        # ------------------------
        self.metadata_table = dynamodb.Table(
            self, "ModelMetadata",
            partition_key={"name": "model_id", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # ------------------------
        # Minimal Lambda for API integration
        # ------------------------
        demo_lambda = lambda_.Function(
            self, "DemoLambda",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="lambda_handler.main",
            code=lambda_.Code.from_inline(
                "def main(event, context):\n"
                "    return {'statusCode': 200, 'body': 'Hello from Model Registry'}"
            ),
        )

        # ------------------------
        # API Gateway
        # ------------------------
        api = apigw.RestApi(
            self, "ModelRegistryApi",
            rest_api_name="Model Registry API",
            description="API for Model Registry"
        )

        # Minimal resource + method to satisfy CDK deployment
        lambda_integration = apigw.LambdaIntegration(demo_lambda)
        models_resource = api.root.add_resource("models")
        models_resource.add_method("GET", lambda_integration)

        # ------------------------
        # Outputs for easy verification
        # ------------------------
        CfnOutput(self, "BucketName", value=self.model_bucket.bucket_name)
        CfnOutput(self, "TableName", value=self.metadata_table.table_name)
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "DemoEndpoint", value=f"{api.url}models")
