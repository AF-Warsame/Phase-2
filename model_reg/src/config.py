# src/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class AWSConfig:
    bucket_name: str
    table_name: str
    api_url: str
    region: str

def load_config() -> AWSConfig:
    load_dotenv()
    
    # These will be populated from CDK outputs
    return AWSConfig(
        bucket_name=os.getenv('MODEL_BUCKET_NAME'),
        table_name=os.getenv('MODEL_TABLE_NAME'),
        api_url=os.getenv('API_URL'),
        region=os.getenv('AWS_REGION', 'us-east-1')
    )