# tests/integration/test_rate_endpoint.py
"""Test rate endpoint for missing artifacts"""
import pytest
import json
import os
import sys
from unittest.mock import Mock, patch

# Setup paths
model_reg_src = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.insert(0, model_reg_src)


def test_rate_nonexistent_artifact_returns_404():
    """Test that rating a non-existent artifact returns 404"""
    from api.handlers import handle_artifact_rate, _get_registry_store
    
    # Mock the registry store to return None (artifact not found)
    with patch('api.handlers._get_registry_store') as mock_store:
        mock_instance = Mock()
        mock_instance.rate.return_value = None
        mock_store.return_value = mock_instance
        
        event = {
            "httpMethod": "GET",
            "path": "/artifacts/model/nonexistent-id-12345/rate",
            "body": None,
            "queryStringParameters": None,
            "headers": {}
        }
        
        response = handle_artifact_rate("nonexistent-id-12345", event)
        
        # Should return 404, not 200
        assert response["statusCode"] == 404, f"Expected 404, got {response['statusCode']}"
        
        body = json.loads(response["body"])
        assert "error" in body
        assert "not found" in body["error"].lower()


def test_rate_method_returns_none_for_nonexistent():
    """Test that RegistryStore.rate() returns None for non-existent artifacts"""
    from api.handlers import RegistryStore
    import os
    
    # Set required environment variables
    os.environ['DYNAMODB_TABLE_NAME'] = 'test-artifacts'
    os.environ['S3_BUCKET_NAME'] = 'test-bucket'
    
    # Mock boto3 resources
    with patch('boto3.resource') as mock_resource, \
         patch('boto3.client') as mock_client:
        
        # Mock the table's get_item to return empty (no Item)
        mock_table = Mock()
        mock_table.get_item.return_value = {}  # No 'Item' key means artifact not found
        
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        store = RegistryStore()
        
        # Rate non-existent artifact
        result = store.rate("nonexistent-artifact-xyz")
        
        # Should return None, not a dict with missing fields
        assert result is None, f"Expected None, got {result}"


def test_rate_existing_artifact_has_required_fields():
    """Test that rating an existing artifact returns all required fields"""
    from api.handlers import RegistryStore
    import os
    
    # Set required environment variables
    os.environ['DYNAMODB_TABLE_NAME'] = 'test-artifacts'
    os.environ['S3_BUCKET_NAME'] = 'test-bucket'
    
    # Mock boto3 resources
    with patch('boto3.resource') as mock_resource, \
         patch('boto3.client') as mock_client:
        
        # Mock the table's get_item to return a valid artifact
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'artifact_id': 'test-artifact-123',
                'name': 'TestModel',
                'artifact_type': 'model',
                'license': 'MIT',
                'size_bytes': 1024000,
                'rating': {
                    'rating_score': 0.9,
                    'reproducibility_score': 0.8,
                    'reviewedness_score': 0.7,
                    'tree_score': 0.6
                }
            }
        }
        
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        store = RegistryStore()
        
        # Rate existing artifact
        result = store.rate("test-artifact-123")
        
        # Should return a dict with all required fields
        assert result is not None, "Result should not be None for existing artifact"
        assert isinstance(result, dict), "Result should be a dict"
        
        # Check required fields per OpenAPI spec
        required_fields = [
            'name', 'category', 'net_score', 'net_score_latency',
            'ramp_up_time', 'ramp_up_time_latency',
            'bus_factor', 'bus_factor_latency',
            'performance_claims', 'performance_claims_latency',
            'license', 'license_latency',
            'dataset_and_code_score', 'dataset_and_code_score_latency',
            'dataset_quality', 'dataset_quality_latency',
            'code_quality', 'code_quality_latency',
            'reproducibility', 'reproducibility_latency',
            'reviewedness', 'reviewedness_latency',
            'tree_score', 'tree_score_latency',
            'size_score', 'size_score_latency'
        ]
        
        for field in required_fields:
            assert field in result, f"Required field '{field}' is missing from rating response"
        
        # Verify name is correct
        assert result['name'] == 'TestModel', f"Expected name 'TestModel', got '{result['name']}'"
        
        # Verify size_score has required platform fields
        assert 'raspberry_pi' in result['size_score']
        assert 'jetson_nano' in result['size_score']
        assert 'desktop_pc' in result['size_score']
        assert 'aws_server' in result['size_score']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
