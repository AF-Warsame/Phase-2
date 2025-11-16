# tests/integration/test_api_handlers.py
import pytest
import json
import os
import sys

# Setup paths
model_reg_src = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.insert(0, model_reg_src)


def test_import_handlers():
    """Test that handlers module can be imported"""
    from api import handlers
    assert handlers is not None
    assert hasattr(handlers, 'lambda_handler')


def test_health_check_function():
    """Test health check function directly"""
    from api.handlers import handle_health_check
    
    response = handle_health_check()
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert "timestamp" in body
    assert body["service"] == "Model Registry API"


def test_success_response_helper():
    """Test success response helper function"""
    from api.handlers import success_response
    
    data = {"message": "Success"}
    response = success_response(data)
    
    assert response["statusCode"] == 200
    assert "Content-Type" in response["headers"]
    assert response["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(response["body"])
    assert body == data


def test_error_response_helper():
    """Test error response helper function"""
    from api.handlers import error_response
    
    response = error_response(404, "Not Found", "corr-123")
    
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert body["error"] == "Not Found"
    assert body["correlation_id"] == "corr-123"


def test_lambda_handler_health_endpoint():
    """Test Lambda handler health endpoint"""
    from api.handlers import lambda_handler
    
    event = {
        "httpMethod": "GET",
        "path": "/health",
        "body": None,
        "queryStringParameters": None
    }
    
    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "healthy"


def test_lambda_handler_not_found():
    """Test Lambda handler returns 404 for unknown endpoint"""
    from api.handlers import lambda_handler
    
    event = {
        "httpMethod": "GET",
        "path": "/unknown",
        "body": None,
        "queryStringParameters": None
    }
    
    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 404


def test_license_check_compatible():
    """Test license compatibility check for compatible license"""
    from api.handlers import lambda_handler
    
    event = {
        "httpMethod": "GET",
        "path": "/license-check",
        "body": None,
        "queryStringParameters": {"license": "MIT"}
    }
    
    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["license"] == "MIT"
    assert body["compatible_with_lgplv2_1"] is True


def test_license_check_incompatible():
    """Test license compatibility check for incompatible license"""
    from api.handlers import lambda_handler
    
    event = {
        "httpMethod": "GET",
        "path": "/license-check",
        "body": None,
        "queryStringParameters": {"license": "GPL-3.0"}
    }
    
    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["license"] == "GPL-3.0"
    assert body["compatible_with_lgplv2_1"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
