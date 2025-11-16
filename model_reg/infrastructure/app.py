# infrastructure/app.py
#!/usr/bin/env python3
import os
from aws_cdk import App
from model_registry.model_registry_stack import ModelRegistryStack

app = App()
ModelRegistryStack(app, "ModelRegistryDev")
app.synth()