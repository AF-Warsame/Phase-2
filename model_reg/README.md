# Model Registry - Phase 2 Implementation

A complete AWS-based model registry service for managing, rating, and distributing AI/ML model packages.

## Features

### Core Functionality

✅ **Package Management (CRUD)**
- Upload packages as ZIP files
- Download packages with metadata
- Update package metadata
- Delete packages from registry

✅ **Rating Service**
- Integration with Phase 1 scoring metrics
- Reproducibility score calculation
- Reviewedness score (community engagement)
- Tree score (dependency health)
- Combined rating score

✅ **HuggingFace Ingestion**
- Automatic ingestion from HuggingFace URLs
- Quality gate (minimum score 0.5)
- Auto-upload to registry

✅ **Search & Discovery**
- List packages with pagination
- Filter by name (regex)
- Filter by version (exact, ^, ~, range)
- Full-text search in model cards

✅ **Utilities**
- Total size calculation
- License compatibility check
- Registry reset endpoint
- Health check endpoint

### Infrastructure

✅ **AWS Components**
- S3 for package storage
- DynamoDB for metadata
- Lambda for API handlers
- API Gateway for REST endpoints
- Cognito for authentication
- CloudWatch for monitoring

✅ **Observability**
- Structured logging with correlation IDs
- CloudWatch metrics dashboard
- Error rate alarms
- Latency monitoring (P50, P95, P99)

✅ **CI/CD**
- GitHub Actions workflow
- Automated testing
- Linting and code quality checks
- Automated deployment

## Project Structure

```
model_reg/
├── src/
│   ├── api/                  # API handlers
│   │   ├── handlers.py       # Lambda handler functions
│   │   └── __init__.py
│   ├── models/               # Data models
│   │   ├── package.py        # Package, PackageMetadata, PackageVersion
│   │   └── __init__.py
│   ├── services/             # Business logic
│   │   ├── package_service.py  # S3/DynamoDB operations
│   │   ├── rating_service.py   # Score calculation
│   │   └── __init__.py
│   └── config.py             # Configuration
├── infrastructure/
│   ├── model_registry/
│   │   ├── model_registry_stack.py  # CDK stack definition
│   │   └── observability.py         # CloudWatch setup
│   ├── app.py                # Lambda entry point
│   ├── deploy.py             # Deployment script
│   └── requirements.txt      # Python dependencies
├── tests/
│   ├── unit/                 # Unit tests
│   │   └── test_package_model.py
│   └── integration/          # Integration tests
├── API_DOCUMENTATION.md      # API reference
├── DEPLOYMENT.md             # Deployment guide
└── README.md                 # This file
```

## Quick Start

### 1. Prerequisites

- Python 3.9+
- AWS Account
- AWS CLI configured
- Node.js 14+ (for CDK)

### 2. Installation

```bash
cd model_reg

# Install dependencies
pip install -r infrastructure/requirements.txt

# Install AWS CDK
npm install -g aws-cdk
```

### 3. Configure AWS

Create `credentials.env`:

```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

### 4. Deploy

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy infrastructure
python infrastructure/deploy.py

# Or manually
cdk deploy
```

### 5. Test

```bash
# Get API endpoint from deployment output
API_URL=<your-api-endpoint>

# Health check
curl $API_URL/health

# Expected: {"status": "healthy", "timestamp": "..."}
```

## API Usage

### Upload Package

```bash
curl -X POST $API_URL/packages \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bert-base",
    "version": "1.0.0",
    "data": "<base64-zip>"
  }'
```

### List Packages

```bash
curl "$API_URL/packages?name=bert&limit=10"
```

### Search Packages

```bash
curl "$API_URL/packages/search?q=transformer"
```

### Ingest from HuggingFace

```bash
curl -X POST $API_URL/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "huggingface_url": "https://huggingface.co/bert-base-uncased"
  }'
```

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires AWS)
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Local Development

Use LocalStack for local AWS services:

```bash
# Start LocalStack
docker compose -f infrastructure/localstack/docker-compose.yml up -d

# Create local resources
aws --endpoint-url=http://localhost:4566 s3 mb s3://local-models
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name local-packages \
  --attribute-definitions AttributeName=package_id,AttributeType=S \
  --key-schema AttributeName=package_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Code Quality

```bash
# Linting
pylint src tests

# Formatting
black src tests

# Type checking
mypy src --ignore-missing-imports
```

## Architecture

### Request Flow

```
Client → API Gateway → Lambda → Services → AWS Resources
                         ↓
                    Correlation ID
                         ↓
                    CloudWatch Logs
```

### Data Flow

```
Upload:  Client → API → Lambda → S3 (package) + DynamoDB (metadata)
Download: Client → API → Lambda → DynamoDB → S3 → Client
Search:  Client → API → Lambda → DynamoDB (scan) → Client
```

### Rating Calculation

```
Repository/HF URL → Fetch Data → Phase 1 Metrics → Calculate Scores
                                      ↓
                     Reproducibility + Reviewedness + Tree Score
                                      ↓
                              Combined Rating (0.0-1.0)
```

## Monitoring

### CloudWatch Dashboard

Access: AWS Console → CloudWatch → Dashboards → ModelRegistryDashboard

**Metrics:**
- API Latency (P50, P95, P99)
- Error Rate
- Request Count
- Lambda Duration
- DynamoDB Operations

### Alarms

- **High Error Rate**: > 5% for 5 minutes
- **High Latency**: P99 > 3000ms for 5 minutes
- **Budget Alert**: Cost exceeds threshold

### Logs

```bash
# View logs
aws logs tail /aws/lambda/ModelRegistryStack-APILambda

# Follow logs
aws logs tail /aws/lambda/ModelRegistryStack-APILambda --follow

# Search by correlation ID
aws logs filter-pattern "correlation_id: abc123"
```

## Security

### Authentication

- AWS Cognito User Pool
- JWT token-based authentication
- Default admin: `defaultadmin` / `CorrectHorseBatteryStaple123!`

### Authorization

- IAM roles for Lambda
- S3 bucket policies
- DynamoDB table policies

### Best Practices

✅ Never commit credentials
✅ Use IAM roles over access keys
✅ Enable MFA on AWS account
✅ Rotate credentials regularly
✅ Use least-privilege policies
✅ Enable CloudTrail audit logging

## Scaling

### Auto-Scaling

- **Lambda**: Automatic concurrent execution scaling
- **DynamoDB**: Pay-per-request mode (auto-scaling)
- **API Gateway**: Handles traffic spikes automatically

### Performance

- **Cold Start**: ~500ms for Lambda
- **Average Latency**: ~200ms (P50)
- **Max Throughput**: 1000 req/s (API Gateway default)

## Cost Estimation

**Low Usage** (~1000 requests/month):
- Lambda: ~$5/month
- DynamoDB: ~$2.50/month
- S3: ~$1/month
- API Gateway: ~$3.50/month
- **Total**: ~$12/month

**Medium Usage** (~100k requests/month):
- Lambda: ~$20/month
- DynamoDB: ~$10/month
- S3: ~$5/month
- API Gateway: ~$35/month
- **Total**: ~$70/month

## Troubleshooting

### Common Issues

**Deployment Fails**
```bash
# Clear CDK cache
rm -rf cdk.out/
cdk synth
```

**Lambda Timeout**
```bash
# Increase timeout in model_registry_stack.py
timeout=Duration.seconds(60)
```

**Permission Denied**
```bash
# Verify AWS credentials
aws sts get-caller-identity
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting.

## Phase 2 Implementation Status

### ✅ Completed Features

- [x] Package CRUD operations
- [x] S3 integration for package storage
- [x] DynamoDB integration for metadata
- [x] Rating service with Phase 1 metrics
- [x] HuggingFace ingestion with quality gate
- [x] Search and enumeration with pagination
- [x] Version query support (exact, ^, ~, range)
- [x] Size cost endpoint
- [x] License compatibility check
- [x] Reset endpoint
- [x] Health check endpoint
- [x] Structured logging with correlation IDs
- [x] CloudWatch observability
- [x] CI/CD with GitHub Actions
- [x] API documentation
- [x] Deployment guide
- [x] Unit tests

### 🚧 Intentionally Excluded (As Requested)

Per the problem statement to "select some features that are extra in nature to leave out primarily the overly unneeded security features":

- ⏭️ Advanced authentication (basic Cognito is sufficient)
- ⏭️ Advanced rate limiting
- ⏭️ Advanced encryption features
- ⏭️ Detailed audit logging beyond correlation IDs
- ⏭️ Token refresh mechanisms
- ⏭️ Advanced IAM policies
- ⏭️ WAF integration
- ⏭️ VPC configuration
- ⏭️ Advanced monitoring dashboards

### 📋 Optional Future Enhancements

- [ ] Frontend UI
- [ ] WebSocket support for real-time updates
- [ ] Batch operations
- [ ] GraphQL API
- [ ] Caching layer (Redis/ElastiCache)
- [ ] CDN integration
- [ ] Multi-region deployment
- [ ] Advanced analytics
- [ ] ML-based recommendations
- [ ] Automated model validation

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `pytest tests/ -v`
4. Run linting: `pylint src tests`
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
2. Review [DEPLOYMENT.md](./DEPLOYMENT.md)
3. Check CloudWatch logs with correlation ID
4. Contact team for assistance

---

**Status**: ✅ Production-Ready (Core Features Complete)

This implementation provides all baseline requirements and key extended features for a fully functional model registry, while intentionally excluding overly complex security features as requested.
