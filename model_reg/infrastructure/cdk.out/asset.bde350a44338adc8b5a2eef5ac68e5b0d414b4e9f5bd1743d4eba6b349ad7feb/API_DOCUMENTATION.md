# Model Registry API Documentation

## Overview

The Model Registry provides a REST API for managing AI/ML model packages with integrated quality scoring, version management, and HuggingFace integration.

## Base URL

```
https://api.model-registry.example.com
```

## Authentication

Authentication is handled via AWS Cognito. Include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Default admin credentials (for testing):
- Username: `defaultadmin`
- Password: `CorrectHorseBatteryStaple123!`

## Endpoints

### Packages

#### Upload Package

Upload a new package to the registry.

**Request:**
```http
POST /packages
Content-Type: application/json

{
  "name": "bert-base-uncased",
  "version": "1.0.0",
  "description": "BERT base model uncased",
  "author": "Google Research",
  "license": "Apache-2.0",
  "repository_url": "https://github.com/google-research/bert",
  "huggingface_url": "https://huggingface.co/bert-base-uncased",
  "model_card": "# BERT Base Uncased\n\nDescription...",
  "tags": ["nlp", "transformer", "bert"],
  "dependencies": ["torch>=1.9.0", "transformers>=4.0.0"],
  "data": "<base64-encoded-zip-file>"
}
```

**Response:**
```json
{
  "message": "Package uploaded successfully",
  "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "package": {
    "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "bert-base-uncased",
    "version": "1.0.0",
    "rating_score": 0.85,
    "reproducibility_score": 0.75,
    "reviewedness_score": 0.90,
    "tree_score": 0.80,
    "size_bytes": 438016384,
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
}
```

#### Get Package

Retrieve package metadata and download link.

**Request:**
```http
GET /packages/{package_id}
```

**Response:**
```json
{
  "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "bert-base-uncased",
  "version": "1.0.0",
  "description": "BERT base model uncased",
  "rating_score": 0.85,
  "data": "<base64-encoded-zip-file>"
}
```

#### Update Package Metadata

Update package metadata (version and data cannot be changed).

**Request:**
```http
PUT /packages/{package_id}
Content-Type: application/json

{
  "description": "Updated description",
  "tags": ["nlp", "transformer", "bert", "updated"],
  "rating_score": 0.87
}
```

**Response:**
```json
{
  "message": "Package updated successfully",
  "package": {
    "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "description": "Updated description",
    "updated_at": "2024-01-15T11:00:00.000Z"
  }
}
```

#### Delete Package

Delete a package from the registry.

**Request:**
```http
DELETE /packages/{package_id}
```

**Response:**
```json
{
  "message": "Package deleted successfully"
}
```

#### List Packages

List packages with optional filtering and pagination.

**Request:**
```http
GET /packages?name=bert&version=^1.0.0&limit=50&next_key=abc123
```

**Query Parameters:**
- `name` (optional): Regex pattern to filter by package name
- `version` (optional): Version query (`1.0.0`, `^1.0.0`, `~1.2.0`, `1.0.0-2.0.0`)
- `limit` (optional): Maximum number of results (default: 100)
- `next_key` (optional): Pagination key from previous response

**Response:**
```json
{
  "packages": [
    {
      "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "bert-base-uncased",
      "version": "1.0.0",
      "rating_score": 0.85
    }
  ],
  "count": 1,
  "next_key": "xyz789"
}
```

#### Search Packages

Search packages by name or model card content.

**Request:**
```http
GET /packages/search?q=transformer
```

**Query Parameters:**
- `q` (required): Search query text

**Response:**
```json
{
  "packages": [
    {
      "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "bert-base-uncased",
      "description": "BERT base model using transformer architecture"
    }
  ],
  "count": 1
}
```

### Ingestion

#### Ingest from HuggingFace

Automatically ingest a package from HuggingFace with quality gate.

**Request:**
```http
POST /ingest
Content-Type: application/json

{
  "huggingface_url": "https://huggingface.co/bert-base-uncased"
}
```

**Response:**
```json
{
  "message": "Package ingested successfully",
  "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "scores": {
    "rating_score": 0.85,
    "reproducibility_score": 0.75,
    "reviewedness_score": 0.90,
    "tree_score": 0.80
  },
  "package": {
    "package_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "bert-base-uncased",
    "version": "1.0.0"
  }
}
```

**Note:** Packages with rating_score < 0.5 will be rejected.

### Utilities

#### Get Total Size

Get the total size of all packages in the registry.

**Request:**
```http
GET /size
```

**Response:**
```json
{
  "total_size_bytes": 5368709120,
  "total_size_mb": 5120.0,
  "total_size_gb": 5.0
}
```

#### License Compatibility Check

Check if a license is compatible with LGPLv2.1.

**Request:**
```http
GET /license-check?license=Apache-2.0
```

**Response:**
```json
{
  "license": "Apache-2.0",
  "compatible_with_lgplv2_1": true,
  "compatible_licenses": [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "ISC", "LGPLv2.1", "LGPL-2.1", "Python-2.0"
  ]
}
```

#### Reset Registry

Reset the registry to empty state (admin only).

**Request:**
```http
POST /reset
```

**Response:**
```json
{
  "message": "Registry reset successfully"
}
```

#### Health Check

Check API health status.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Model Registry API"
}
```

## Version Queries

The API supports several version query formats:

- **Exact**: `1.2.3` - Matches exactly version 1.2.3
- **Caret**: `^1.2.3` - Compatible with 1.2.3 (same major version, >= minor.patch)
- **Tilde**: `~1.2.3` - Approximately equivalent (same major.minor, >= patch)
- **Range**: `1.0.0-2.0.0` - Between 1.0.0 and 2.0.0 (inclusive)

## Rating Scores

Each package receives four quality scores:

- **rating_score**: Overall quality score (0.0-1.0)
  - Combines Phase 1 NetScore with additional metrics
  - Weighted: 40% base score + 20% reproducibility + 20% reviewedness + 20% tree score

- **reproducibility_score**: Ability to reproduce results (0.0-1.0)
  - Based on code availability, dataset quality, documentation

- **reviewedness_score**: Community review and engagement (0.0-1.0)
  - Based on stars, forks, issues, PR activity

- **tree_score**: Dependency health (0.0-1.0)
  - Based on dependency freshness, known vulnerabilities

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Status Codes:**
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Observability

All requests include a correlation ID for tracing. Check CloudWatch logs using the correlation ID to debug issues.

**CloudWatch Dashboard:** Available at AWS Console > CloudWatch > Dashboards > ModelRegistryDashboard

**Metrics:**
- API latency (P50, P95, P99)
- Error rate
- Request count
- S3 egress

## Rate Limits

Default rate limits (configurable):
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Examples

### Python

```python
import requests
import base64

# Upload package
with open('model.zip', 'rb') as f:
    zip_data = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    'https://api.model-registry.example.com/packages',
    json={
        'name': 'my-model',
        'version': '1.0.0',
        'data': zip_data
    },
    headers={'Authorization': 'Bearer <token>'}
)

package = response.json()
print(f"Package ID: {package['package_id']}")

# List packages
response = requests.get(
    'https://api.model-registry.example.com/packages',
    params={'name': 'bert', 'limit': 10}
)

packages = response.json()
print(f"Found {packages['count']} packages")
```

### cURL

```bash
# Health check
curl https://api.model-registry.example.com/health

# List packages
curl -H "Authorization: Bearer <token>" \
  "https://api.model-registry.example.com/packages?limit=10"

# Search packages
curl -H "Authorization: Bearer <token>" \
  "https://api.model-registry.example.com/packages/search?q=transformer"

# Get package
curl -H "Authorization: Bearer <token>" \
  "https://api.model-registry.example.com/packages/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```
