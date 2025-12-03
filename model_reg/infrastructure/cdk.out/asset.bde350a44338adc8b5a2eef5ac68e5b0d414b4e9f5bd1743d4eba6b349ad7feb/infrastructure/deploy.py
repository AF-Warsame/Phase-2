# infrastructure/deploy.py
import os
from pathlib import Path
from dotenv import load_dotenv
import boto3
import json


def load_credentials():
    """Load AWS credentials from root directory credentials.env"""
    # Get root directory (two levels up from current file)
    root_dir = Path(__file__).parent.parent
    credentials_path = root_dir / "credentials.env"

    if not credentials_path.exists():
        print(f"Credentials file not found at: {credentials_path}")
        return False

    # Load credentials
    load_dotenv(credentials_path)

    # Verify credentials were loaded
    if not all(
        [
            os.getenv("AWS_ACCESS_KEY_ID"),
            os.getenv("AWS_SECRET_ACCESS_KEY"),
            os.getenv("AWS_REGION"),
        ]
    ):
        print("Required AWS credentials not found in credentials.env")
        return False

    return True


def verify_aws_credentials():
    """Verify AWS credentials are working"""
    if not load_credentials():
        return False

    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        identity = sts.get_caller_identity()
        print(f"AWS Credentials Valid - Account: {identity['Account']}")
        return True
    except Exception as e:
        print(f"AWS Credentials Error: {str(e)}")
        return False


def deploy_infrastructure():
    """Deploy the CDK stack"""
    if not verify_aws_credentials():
        return

    try:
        # Set AWS credentials as environment variables for CDK
        os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        os.environ["AWS_REGION"] = os.getenv("AWS_REGION", "us-east-1")

        print("Deploying infrastructure...")
        os.system("cdk deploy --require-approval never")
        print("Infrastructure deployed successfully")
    except Exception as e:
        print(f"Deployment Error: {str(e)}")


if __name__ == "__main__":
    deploy_infrastructure()
