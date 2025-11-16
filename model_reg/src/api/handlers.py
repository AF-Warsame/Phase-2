# src/api/handlers.py
import json
import logging
import uuid
import base64
from datetime import datetime
from typing import Dict, Any
import os
import sys

# Handle imports for both Lambda and testing environments
try:
    from ..services import PackageService, RatingService
    from ..models import PackageMetadata
except ImportError:
    # Fallback for direct execution or testing
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from services import PackageService, RatingService
    from models import PackageMetadata

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services - lazy initialization to avoid AWS connection in testing
package_service = None
rating_service = None

def _get_package_service():
    """Lazy initialization of package service"""
    global package_service
    if package_service is None:
        package_service = PackageService()
    return package_service

def _get_rating_service():
    """Lazy initialization of rating service"""
    global rating_service
    if rating_service is None:
        rating_service = RatingService()
    return rating_service


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for API Gateway events"""
    
    # Generate correlation ID for tracing
    correlation_id = str(uuid.uuid4())
    logger.info(f"Request started - CorrelationID: {correlation_id}")
    
    try:
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        
        # Route to appropriate handler
        if path == "/packages":
            if method == "POST":
                return handle_upload_package(event, correlation_id)
            elif method == "GET":
                return handle_list_packages(event, correlation_id)
        
        elif path.startswith("/packages/"):
            package_id = path.split("/")[-1]
            
            if method == "GET":
                return handle_get_package(package_id, correlation_id)
            elif method == "PUT":
                return handle_update_package(package_id, event, correlation_id)
            elif method == "DELETE":
                return handle_delete_package(package_id, correlation_id)
        
        elif path == "/packages/search":
            return handle_search_packages(event, correlation_id)
        
        elif path == "/ingest":
            return handle_ingest_from_huggingface(event, correlation_id)
        
        elif path == "/size":
            return handle_get_total_size(correlation_id)
        
        elif path == "/license-check":
            return handle_license_check(event, correlation_id)
        
        elif path == "/reset":
            return handle_reset(correlation_id)
        
        elif path == "/health":
            return handle_health_check()
        
        return error_response(404, "Not Found", correlation_id)
        
    except Exception as e:
        logger.error(f"Unhandled error - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, "Internal Server Error", correlation_id)


def handle_upload_package(event: Dict, correlation_id: str) -> Dict:
    """Handle POST /packages - Upload a new package"""
    try:
        body = json.loads(event.get("body", "{}"))
        
        # Extract metadata
        name = body.get("name")
        version = body.get("version")
        
        if not name or not version:
            return error_response(400, "Missing required fields: name, version", correlation_id)
        
        # Get package data (base64 encoded zip)
        package_data_b64 = body.get("data")
        if not package_data_b64:
            return error_response(400, "Missing package data", correlation_id)
        
        # Decode zip data
        zip_data = base64.b64decode(package_data_b64)
        
        # Create metadata
        metadata = PackageMetadata(
            name=name,
            version=version,
            description=body.get("description"),
            author=body.get("author"),
            license=body.get("license"),
            repository_url=body.get("repository_url"),
            huggingface_url=body.get("huggingface_url"),
            model_card=body.get("model_card"),
            tags=body.get("tags", []),
            dependencies=body.get("dependencies", [])
        )
        
        # Calculate ratings if URL provided
        if metadata.repository_url or metadata.huggingface_url:
            scores = _get_rating_service().calculate_rating(
                repository_url=metadata.repository_url,
                huggingface_url=metadata.huggingface_url
            )
            metadata.rating_score = scores.get("rating_score")
            metadata.reproducibility_score = scores.get("reproducibility_score")
            metadata.reviewedness_score = scores.get("reviewedness_score")
            metadata.tree_score = scores.get("tree_score")
        
        # Create package
        package = _get_package_service().create_package(metadata, zip_data)
        
        logger.info(f"Package created - CorrelationID: {correlation_id} - ID: {package.package_id}")
        
        return success_response({
            "message": "Package uploaded successfully",
            "package_id": package.package_id,
            "package": package.to_dict()
        }, 201)
        
    except Exception as e:
        logger.error(f"Upload failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, f"Upload failed: {str(e)}", correlation_id)


def handle_get_package(package_id: str, correlation_id: str) -> Dict:
    """Handle GET /packages/{id} - Get package details and download link"""
    try:
        package = _get_package_service().get_package(package_id)
        
        if not package:
            return error_response(404, "Package not found", correlation_id)
        
        # Get download data
        package_data = _get_package_service().get_package_data(package_id)
        
        response = package.to_dict()
        if package_data:
            # Return base64 encoded data
            response["data"] = base64.b64encode(package_data).decode('utf-8')
        
        return success_response(response)
        
    except Exception as e:
        logger.error(f"Get package failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_update_package(package_id: str, event: Dict, correlation_id: str) -> Dict:
    """Handle PUT /packages/{id} - Update package metadata"""
    try:
        body = json.loads(event.get("body", "{}"))
        
        package = _get_package_service().update_package_metadata(package_id, body)
        
        if not package:
            return error_response(404, "Package not found", correlation_id)
        
        logger.info(f"Package updated - CorrelationID: {correlation_id} - ID: {package_id}")
        
        return success_response({
            "message": "Package updated successfully",
            "package": package.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Update failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_delete_package(package_id: str, correlation_id: str) -> Dict:
    """Handle DELETE /packages/{id} - Delete package"""
    try:
        success = _get_package_service().delete_package(package_id)
        
        if not success:
            return error_response(404, "Package not found", correlation_id)
        
        logger.info(f"Package deleted - CorrelationID: {correlation_id} - ID: {package_id}")
        
        return success_response({"message": "Package deleted successfully"}, 204)
        
    except Exception as e:
        logger.error(f"Delete failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_list_packages(event: Dict, correlation_id: str) -> Dict:
    """Handle GET /packages - List packages with filtering and pagination"""
    try:
        params = event.get("queryStringParameters") or {}
        
        name_regex = params.get("name")
        version_query = params.get("version")
        limit = int(params.get("limit", "100"))
        last_key = params.get("next_key")
        
        result = _get_package_service().list_packages(
            name_regex=name_regex,
            version_query=version_query,
            limit=limit,
            last_key=last_key
        )
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"List failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_search_packages(event: Dict, correlation_id: str) -> Dict:
    """Handle GET /packages/search - Search packages by text"""
    try:
        params = event.get("queryStringParameters") or {}
        search_text = params.get("q", "")
        
        if not search_text:
            return error_response(400, "Missing search query 'q'", correlation_id)
        
        packages = _get_package_service().search_packages(search_text)
        
        return success_response({
            "packages": [p.to_dict() for p in packages],
            "count": len(packages)
        })
        
    except Exception as e:
        logger.error(f"Search failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_ingest_from_huggingface(event: Dict, correlation_id: str) -> Dict:
    """Handle POST /ingest - Ingest package from HuggingFace with quality gate"""
    try:
        body = json.loads(event.get("body", "{}"))
        hf_url = body.get("huggingface_url")
        
        if not hf_url:
            return error_response(400, "Missing huggingface_url", correlation_id)
        
        # Calculate rating
        scores = _get_rating_service().calculate_rating(huggingface_url=hf_url)
        
        # Check quality threshold
        if not _get_rating_service().meets_quality_threshold(scores, threshold=0.5):
            return error_response(400, 
                f"Package does not meet quality threshold. Rating: {scores.get('rating_score', 0.0)}", 
                correlation_id)
        
        # Auto-generate package from HuggingFace
        # In production, this would download the actual model files
        # For now, create a placeholder
        parts = hf_url.rstrip('/').split('/')
        model_name = parts[-1]
        
        metadata = PackageMetadata(
            name=model_name,
            version="1.0.0",
            huggingface_url=hf_url,
            rating_score=scores.get("rating_score"),
            reproducibility_score=scores.get("reproducibility_score"),
            reviewedness_score=scores.get("reviewedness_score"),
            tree_score=scores.get("tree_score")
        )
        
        # Create minimal zip package
        import io
        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('README.md', f'# {model_name}\n\nIngested from {hf_url}')
        
        package = _get_package_service().create_package(metadata, zip_buffer.getvalue())
        
        logger.info(f"Package ingested - CorrelationID: {correlation_id} - HF: {hf_url}")
        
        return success_response({
            "message": "Package ingested successfully",
            "package_id": package.package_id,
            "scores": scores,
            "package": package.to_dict()
        }, 201)
        
    except Exception as e:
        logger.error(f"Ingest failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_get_total_size(correlation_id: str) -> Dict:
    """Handle GET /size - Get total size of all packages"""
    try:
        total_bytes = _get_package_service().get_total_size()
        
        return success_response({
            "total_size_bytes": total_bytes,
            "total_size_mb": round(total_bytes / (1024 * 1024), 2),
            "total_size_gb": round(total_bytes / (1024 * 1024 * 1024), 3)
        })
        
    except Exception as e:
        logger.error(f"Get size failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_license_check(event: Dict, correlation_id: str) -> Dict:
    """Handle GET /license-check - Check license compatibility"""
    try:
        params = event.get("queryStringParameters") or {}
        license_name = params.get("license", "")
        
        # Define compatible licenses with LGPLv2.1
        compatible_licenses = [
            "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
            "ISC", "LGPLv2.1", "LGPL-2.1", "Python-2.0"
        ]
        
        is_compatible = license_name in compatible_licenses
        
        return success_response({
            "license": license_name,
            "compatible_with_lgplv2_1": is_compatible,
            "compatible_licenses": compatible_licenses
        })
        
    except Exception as e:
        logger.error(f"License check failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_reset(correlation_id: str) -> Dict:
    """Handle POST /reset - Reset registry to empty state"""
    try:
        success = _get_package_service().reset_registry()
        
        if success:
            logger.info(f"Registry reset - CorrelationID: {correlation_id}")
            return success_response({"message": "Registry reset successfully"})
        else:
            return error_response(500, "Reset failed", correlation_id)
        
    except Exception as e:
        logger.error(f"Reset failed - CorrelationID: {correlation_id} - {str(e)}")
        return error_response(500, str(e), correlation_id)


def handle_health_check() -> Dict:
    """Handle GET /health - Health check endpoint"""
    return success_response({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Model Registry API"
    })


def success_response(data: Dict, status_code: int = 200) -> Dict:
    """Create a successful response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }


def error_response(status_code: int, message: str, correlation_id: str = None) -> Dict:
    """Create an error response"""
    body = {"error": message}
    if correlation_id:
        body["correlation_id"] = correlation_id
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }
