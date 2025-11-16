#!/usr/bin/env python3
# infrastructure/cdk_app.py
"""CDK App initialization file"""

from aws_cdk import App, Environment
from model_registry.model_registry_stack import ModelRegistryStack
from model_registry.observability import ObservabilityStack
import os

app = App()

# Get environment from context or use default
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
)

# Create the main stack
model_registry_stack = ModelRegistryStack(
    app,
    "ModelRegistryStack",
    env=env,
    description="Model Registry Infrastructure - Phase 2"
)

# Create observability stack
observability_stack = ObservabilityStack(
    app,
    "ModelRegistryObservabilityStack",
    lambda_function=model_registry_stack.api_lambda,
    env=env,
    description="Observability and monitoring for Model Registry"
)

app.synth()
