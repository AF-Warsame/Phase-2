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
    Duration
)
from constructs import Construct

class ModelRegistryStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for model storage
        self.s3_bucket = s3.Bucket(
            self, "S3Bucket",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False
        )

        # DynamoDB table for metadata
        self.dynamodb_table = dynamodb.Table(
            self, "DynamoDBTable",
            partition_key=dynamodb.Attribute(name="model_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Cognito User Pool for authentication
        self.user_pool = cognito.UserPool(
            self, "CognitoUserPool",
            self_sign_up_enabled=False,
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your account for Model Registry",
                email_body="Hello {username}, Thanks for signing up. Your verification code is {####}.",
                email_style=cognito.VerificationEmailStyle.CODE
            )
        )

        # Cognito Default Admin User
        admin_group = self.user_pool.add_group("DefaultAdminGroup")
        self.user_pool.add_user(
            "DefaultAdmin",
            user_name="defaultadmin",
            user_group=admin_group,
            password="CorrectHorseBatteryStaple123!"
        )

        # Lambda Function for the API Handlers
        api_lambda_role = iam.Role(
            self, "APILambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                )
            ]
        )

        self.api_lambda = lambda_.Function(
            self, "APILambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset("infrastructure"),
            environment={
                "S3_BUCKET_NAME": self.s3_bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": self.dynamodb_table.table_name,
                "COGNITO_USER_POOL_ID": self.user_pool.user_pool_id
            },
            timeout=Duration.seconds(30),
            role=api_lambda_role
        )

        # API Gateway Integration - Use proxy integration for simplicity
        api_gateway = apigw.LambdaRestApi(
            self, "APIGateway",
            rest_api_name="Model Registry API",
            description="API for managing AI/ML model packages with rating and discovery.",
            handler=self.api_lambda,
            proxy=True  # Use proxy integration for all paths
        )

        # CloudWatch Alarm for Error Rate
        error_alarm = apigw.Stage(
            self,
            "ErrorRateAlarm",
            deployment=api_gateway.deployment_stage,
            metrics=[api_gateway.metric_client_error()]
        )

        # SNS Topic for CloudWatch Alarm
        sns_topic = sns.Topic(self, "SNSTopic")
        sns_topic.add_subscription(
            subs.EmailSubscription("your-email@example.com")
        )

        # Outputs
        self.s3_bucket_name_output = self.s3_bucket.bucket_name