# Model Registry Deployment Guide

## Prerequisites

- Python 3.9+
- AWS Account with appropriate permissions
- AWS CLI configured
- Node.js 14+ (for AWS CDK)
- Docker (optional, for local testing)

## Environment Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
cd model_reg
pip install -r infrastructure/requirements.txt

# Install AWS CDK
npm install -g aws-cdk

# Verify installation
cdk --version
```

### 2. Configure AWS Credentials

Create `model_reg/credentials.env` from the template:

```bash
# Copy the example file
cp credentials.env.example credentials.env

# Edit credentials.env and fill in your actual AWS credentials
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# AWS_REGION=us-east-1
```

**Important:** Never commit this file to version control. It's already in `.gitignore`.

### 3. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap aws://ACCOUNT_ID/REGION
```

Replace `ACCOUNT_ID` with your AWS account ID and `REGION` with your target region.

## Deployment

### Option 1: Automated Deployment

```bash
cd model_reg
python infrastructure/deploy.py
```

This script will:
1. Verify AWS credentials
2. Deploy the CDK stack
3. Output the API endpoint URL

### Option 2: Manual CDK Deployment

```bash
cd model_reg

# Synthesize CloudFormation template
cdk synth

# Deploy the stack
cdk deploy --require-approval never

# View outputs
cdk outputs
```

### Expected Outputs

After deployment, you'll receive:

```
ModelRegistryStack.APIEndpoint = https://abc123.execute-api.us-east-1.amazonaws.com/prod
ModelRegistryStack.S3BucketName = modelregistrystack-s3bucket-abc123
ModelRegistryStack.DynamoDBTableName = ModelRegistryStack-DynamoDBTable-ABC123
ModelRegistryStack.UserPoolId = us-east-1_abc123
```

## Infrastructure Components

### 1. S3 Bucket
- **Purpose**: Store package zip files
- **Versioning**: Enabled
- **Retention**: RETAIN (not deleted on stack deletion)
- **Access**: Private, accessed via Lambda IAM role

### 2. DynamoDB Table
- **Purpose**: Store package metadata
- **Billing**: Pay-per-request (auto-scaling)
- **Partition Key**: `package_id`
- **Retention**: RETAIN

### 3. Lambda Function
- **Runtime**: Python 3.9
- **Handler**: `app.lambda_handler`
- **Timeout**: 30 seconds
- **Memory**: 512 MB
- **Environment Variables**:
  - `S3_BUCKET_NAME`
  - `DYNAMODB_TABLE_NAME`
  - `COGNITO_USER_POOL_ID`

### 4. API Gateway
- **Type**: REST API
- **Integration**: Lambda Proxy
- **Endpoints**: See API_DOCUMENTATION.md
- **CORS**: Enabled for all origins

### 5. Cognito User Pool
- **Purpose**: Authentication
- **Admin Group**: Created automatically during deployment
- **Password Policy**: 
  - Min length: 12
  - Requires: lowercase, uppercase, digits, symbols

**Note:** Users must be created after deployment using AWS CLI or Console.

## Post-Deployment Configuration

### 1. Get Deployment Outputs

After deployment completes, get the API endpoint and other resource IDs:

```bash
# View all stack outputs
cdk deploy 2>&1 | grep -A 10 "Outputs:"

# Or query specific outputs
aws cloudformation describe-stacks \
  --stack-name ModelRegistryStack \
  --query 'Stacks[0].Outputs' \
  --output table
```

Save these values - you'll need them for testing:
- **API Endpoint**: The URL for making API requests (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod/`)
- **User Pool ID**: For creating users (e.g., `us-east-1_abc123`)
- **S3 Bucket Name**: For direct S3 access if needed
- **DynamoDB Table Name**: For direct database access if needed

### 2. Create Admin User

Create a default admin user in the Cognito User Pool:

```bash
# Replace <user-pool-id> with the value from stack outputs
USER_POOL_ID="<user-pool-id-from-outputs>"

# Create the admin user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --temporary-password "CorrectHorseBatteryStaple123!" \
  --user-attributes Name=email,Value=admin@example.com \
  --message-action SUPPRESS

# Add user to Admins group
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --group-name Admins

# Set permanent password (optional - otherwise user must change on first login)
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --password "CorrectHorseBatteryStaple123!" \
  --permanent

echo "Admin user 'defaultadmin' created successfully"
```

### 3. Test Deployment

Test the API endpoint to verify deployment:

```bash
# Replace <api-endpoint> with the actual endpoint from stack outputs
API_ENDPOINT="<your-api-endpoint-from-outputs>"

# Health check
curl $API_ENDPOINT/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-01-15T10:30:00.000Z"}
```

If the health check succeeds, your deployment is working correctly!

### 4. Update Environment Variables (Optional)

Create `.env` file in project root for convenience:

```bash
MODEL_BUCKET_NAME=<from-cdk-output>
MODEL_TABLE_NAME=<from-cdk-output>
API_URL=<from-cdk-output>
AWS_REGION=us-east-1
```

## Local Development

### LocalStack Setup

For local testing without AWS costs:

```bash
# Start LocalStack
docker compose -f infrastructure/localstack/docker-compose.yml up -d

# Set environment variables
export S3_BUCKET_NAME=local-models
export DYNAMODB_TABLE_NAME=local-packages
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Create local resources
aws --endpoint-url=http://localhost:4566 s3 mb s3://local-models
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name local-packages \
  --attribute-definitions AttributeName=package_id,AttributeType=S \
  --key-schema AttributeName=package_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Run Lambda locally
python -m model_reg.src.api.handlers
```

## CI/CD with GitHub Actions

### 1. Configure GitHub Secrets

Add these secrets to your repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### 2. OIDC Authentication (Recommended)

For more secure authentication:

```yaml
# In .github/workflows/deploy.yml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole
    aws-region: us-east-1
```

### 3. Deployment Workflow

The CI/CD pipeline automatically:
1. Runs tests on PR
2. Deploys to staging on merge to `develop`
3. Deploys to production on merge to `main`

## Monitoring

### CloudWatch Dashboard

Access at: AWS Console > CloudWatch > Dashboards > ModelRegistryDashboard

**Metrics:**
- API Latency (P50, P95, P99)
- Error Rate
- Request Count
- Lambda Invocations
- DynamoDB Throttles

### Alarms

**Configured Alarms:**
1. **High Error Rate**: Triggers when error rate > 5% for 5 minutes
2. **High Latency**: Triggers when P99 latency > 3000ms for 5 minutes
3. **Budget Alert**: Email notification when costs exceed threshold

**SNS Topics:**
- Error alerts sent to configured email
- Budget alerts sent to team email

### Logs

View logs:
```bash
# API Gateway logs
aws logs tail /aws/lambda/ModelRegistryStack-APILambda

# Real-time monitoring
aws logs tail /aws/lambda/ModelRegistryStack-APILambda --follow
```

## Scaling

### Auto-Scaling

Both DynamoDB and Lambda auto-scale automatically:

- **DynamoDB**: Pay-per-request mode scales automatically
- **Lambda**: Scales to handle concurrent requests (up to account limits)
- **API Gateway**: Automatically handles traffic spikes

### Performance Optimization

1. **Lambda Cold Starts**: Provision concurrent executions for critical endpoints
2. **DynamoDB**: Add GSI for common query patterns
3. **S3**: Enable Transfer Acceleration for large uploads
4. **API Gateway**: Enable caching for read-heavy endpoints

## Cost Management

### Budget Alarms

Set up billing alarms:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name ModelRegistryBudget \
  --alarm-description "Alert when monthly costs exceed $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold
```

### Cost Optimization

1. **S3 Lifecycle Policies**: Archive old packages to Glacier
2. **DynamoDB**: Use on-demand billing for variable workloads
3. **Lambda**: Optimize memory allocation and timeout
4. **CloudWatch**: Reduce log retention period

**Estimated Monthly Costs** (Low Usage):
- Lambda: ~$5
- DynamoDB: ~$2.50
- S3: ~$1
- API Gateway: ~$3.50
- **Total**: ~$12/month

## Troubleshooting

### Common Issues

**1. Deployment Fails**
```bash
# Check CDK version
cdk --version

# Update CDK
npm update -g aws-cdk

# Clear CDK cache
rm -rf cdk.out/
cdk synth
```

**2. Lambda Timeout**
```bash
# Increase timeout in stack
timeout=Duration.seconds(60)

# Redeploy
cdk deploy
```

**3. Permission Denied**
```bash
# Verify IAM permissions
aws sts get-caller-identity

# Check role policies
aws iam get-role --role-name APILambdaExecutionRole
```

**4. Package Upload Fails**
```bash
# Check S3 bucket permissions
aws s3api get-bucket-policy --bucket <bucket-name>

# Test S3 upload
aws s3 cp test.txt s3://<bucket-name>/test.txt
```

### Debug Mode

Enable debug logging:

```python
# In handlers.py
logger.setLevel(logging.DEBUG)
```

### Support

For issues:
1. Check CloudWatch logs for correlation ID
2. Review API_DOCUMENTATION.md for correct usage
3. Verify AWS credentials and permissions
4. Contact team for assistance

## Cleanup

### Remove All Resources

```bash
cd model_reg

# Destroy stack
cdk destroy

# Manually delete S3 bucket (if needed)
aws s3 rb s3://<bucket-name> --force

# Manually delete DynamoDB table (if needed)
aws dynamodb delete-table --table-name <table-name>
```

**Warning:** This will permanently delete all packages and data.

## Security Best Practices

1. **Never commit AWS credentials** to version control
2. **Use IAM roles** instead of access keys where possible
3. **Enable MFA** on AWS root account
4. **Rotate credentials** regularly
5. **Use least-privilege IAM policies**
6. **Enable CloudTrail** for audit logging
7. **Encrypt S3 buckets** at rest
8. **Use VPC** for Lambda in production
9. **Enable WAF** on API Gateway for production
10. **Regular security audits** using AWS Security Hub

## Next Steps

1. Set up staging and production environments
2. Configure custom domain name
3. Implement rate limiting
4. Add request validation
5. Set up monitoring dashboards
6. Configure backup policies
7. Implement disaster recovery plan
8. Performance testing
9. Security audit
10. Documentation review
