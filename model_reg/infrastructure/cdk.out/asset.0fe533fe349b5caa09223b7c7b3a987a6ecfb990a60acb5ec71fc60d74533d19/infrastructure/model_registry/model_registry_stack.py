from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_logs as logs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class ModelRegistryStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for model storage
        self.s3_bucket = s3.Bucket(
            self,
            "S3Bucket",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )

        # DynamoDB table for metadata
        self.dynamodb_table = dynamodb.Table(
            self,
            "DynamoDBTable",
            partition_key=dynamodb.Attribute(
                name="artifact_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Cognito User Pool for authentication
        self.user_pool = cognito.UserPool(
            self,
            "CognitoUserPool",
            self_sign_up_enabled=False,
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your account for Model Registry",
                email_body="Hello {username}, Thanks for signing up. Your verification code is {####}.",
                email_style=cognito.VerificationEmailStyle.CODE,
            ),
        )

        # Cognito Default Admin Group (use L1 construct for compatibility across CDK versions)
        cognito.CfnUserPoolGroup(
            self,
            "DefaultAdminGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="Admins",
        )

        # Note: Creating users via CDK is not recommended for production
        # Users should be created via AWS Console, AWS CLI, or at runtime
        # The deployment guide will provide instructions for creating the default admin user

        # Lambda Function for the API Handlers
        api_lambda_role = iam.Role(
            self,
            "APILambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                ),
            ],
        )

        self.api_lambda = lambda_.Function(
            self,
            "APILambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="infrastructure/app.lambda_handler",
            # Package parent dir so both infrastructure/app.py and src/ are included
            code=lambda_.Code.from_asset(
                "..",
                exclude=[
                    "cdk.out",
                    "*/cdk.out",
                    "build",
                    ".venv",
                    "venv",
                    "**/__pycache__",
                    "**/*.pyc",
                    ".git",
                    ".github",
                    "*.lock",
                ],
            ),
            environment={
                "S3_BUCKET_NAME": self.s3_bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": self.dynamodb_table.table_name,
                "COGNITO_USER_POOL_ID": self.user_pool.user_pool_id,
            },
            timeout=Duration.seconds(30),
            role=api_lambda_role,
        )

        # API Gateway Integration - Use proxy integration for simplicity
        api_gateway = apigw.LambdaRestApi(
            self,
            "APIGateway",
            rest_api_name="Model Registry API",
            description="API for managing AI/ML model packages with rating and discovery.",
            handler=self.api_lambda,
            proxy=True,  # Use proxy integration for all paths
        )

        # Outputs
        self.s3_bucket_name_output = self.s3_bucket.bucket_name
