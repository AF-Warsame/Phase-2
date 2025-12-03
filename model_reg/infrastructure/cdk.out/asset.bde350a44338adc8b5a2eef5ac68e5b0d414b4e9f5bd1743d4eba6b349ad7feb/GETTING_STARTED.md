# Getting Started with Model Registry

This guide will help you deploy the Model Registry to AWS in just a few steps.

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Python 3.9 or higher installed (`python --version`)
- [ ] Node.js 14 or higher installed (`node --version`)
- [ ] AWS Account with admin permissions
- [ ] AWS CLI installed and configured (`aws --version`)
- [ ] Your AWS Access Key ID and Secret Access Key ready

## Step-by-Step Deployment

### Step 1: Navigate to the model_reg Directory

```bash
cd model_reg
```

### Step 2: Create Your Credentials File

**Windows PowerShell:**
```powershell
Copy-Item credentials.env.example credentials.env
notepad credentials.env
```

**Linux/Mac:**
```bash
cp credentials.env.example credentials.env
nano credentials.env
```

Edit the file and replace with your actual AWS credentials:
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

Save and close the file.

### Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r infrastructure/requirements.txt

# Install AWS CDK globally
npm install -g aws-cdk

# Verify CDK installation
cdk --version
```

Expected output: `2.x.x (build xxxxx)`

### Step 4: Bootstrap CDK (First Time Only)

You only need to do this once per AWS account/region combination.

```bash
# Get your AWS account ID
aws sts get-caller-identity --query Account --output text

# Bootstrap CDK (replace 123456789012 with your account ID)
cdk bootstrap aws://123456789012/us-east-1
```

Expected output: `Environment aws://123456789012/us-east-1 bootstrapped.`

### Step 5: Deploy the Infrastructure

```bash
python infrastructure/deploy.py
```

**IMPORTANT:** Watch for the deployment outputs! You'll see something like:

```
✅  ModelRegistryStack

Outputs:
ModelRegistryStack.APIEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
ModelRegistryStack.UserPoolId = us-east-1_abc123XYZ
ModelRegistryStack.S3BucketName = modelregistrystack-s3bucket-abc123
ModelRegistryStack.DynamoDBTableName = ModelRegistryStack-DynamoDBTable-ABC123
```

**Copy and save these values!** You'll need them for the next steps.

### Step 6: Create the Admin User

Replace `YOUR_USER_POOL_ID` with the UserPoolId from Step 5.

**Windows PowerShell:**
```powershell
$USER_POOL_ID = "us-east-1_abc123XYZ"  # Replace with your actual User Pool ID

# Create the admin user
aws cognito-idp admin-create-user `
  --user-pool-id $USER_POOL_ID `
  --username defaultadmin `
  --temporary-password "CorrectHorseBatteryStaple123!" `
  --message-action SUPPRESS

# Add to admin group
aws cognito-idp admin-add-user-to-group `
  --user-pool-id $USER_POOL_ID `
  --username defaultadmin `
  --group-name Admins

# Set permanent password
aws cognito-idp admin-set-user-password `
  --user-pool-id $USER_POOL_ID `
  --username defaultadmin `
  --password "CorrectHorseBatteryStaple123!" `
  --permanent
```

**Linux/Mac:**
```bash
USER_POOL_ID="us-east-1_abc123XYZ"  # Replace with your actual User Pool ID

# Create the admin user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --temporary-password "CorrectHorseBatteryStaple123!" \
  --message-action SUPPRESS

# Add to admin group
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --group-name Admins

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username defaultadmin \
  --password "CorrectHorseBatteryStaple123!" \
  --permanent
```

Expected output: (no error message means success)

### Step 7: Test Your Deployment

Replace `YOUR_API_ENDPOINT` with the APIEndpoint from Step 5.

**Windows PowerShell:**
```powershell
$API_ENDPOINT = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod"

# Test the health endpoint
Invoke-WebRequest -Uri "$API_ENDPOINT/health"
```

**Linux/Mac:**
```bash
API_ENDPOINT="https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod"

# Test the health endpoint
curl $API_ENDPOINT/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-15T10:30:00.000Z"}
```

## Success! 🎉

Your Model Registry is now deployed and running on AWS!

### What You Can Do Next:

1. **Read the API Documentation**: Check `API_DOCUMENTATION.md` for all available endpoints
2. **Try uploading a package**: See examples in `API_DOCUMENTATION.md`
3. **Monitor your deployment**: Check the CloudWatch dashboard in AWS Console
4. **Set up your environment file**: Create a `.env` file with your deployment details for easy reference

### Quick Reference

Your deployment details (save these!):

```
API Endpoint: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
User Pool ID: us-east-1_abc123XYZ
Admin Username: defaultadmin
Admin Password: CorrectHorseBatteryStaple123!
```

## Troubleshooting

### Problem: "credentials.env.example not found"

**Solution:** Make sure you're in the `model_reg` directory:
```bash
cd model_reg
ls credentials.env.example  # Should show the file
```

### Problem: "cdk: command not found"

**Solution:** Install AWS CDK globally:
```bash
npm install -g aws-cdk
```

### Problem: "Cannot find path... Invalid URI"

**Solution:** Make sure you're using the **actual values** from your deployment output, not the placeholder text like `<api-endpoint>` or `YOUR_USER_POOL_ID`.

### Problem: "An error occurred (UserNotFoundException)"

**Solution:** This usually means the user was already created. Try logging in with the existing credentials, or delete and recreate:
```bash
aws cognito-idp admin-delete-user --user-pool-id $USER_POOL_ID --username defaultadmin
# Then run the create user commands again
```

### More Help

For detailed troubleshooting, see:
- `DEPLOYMENT.md` - Complete deployment guide with advanced options
- `API_DOCUMENTATION.md` - API reference
- `README.md` - Project overview and architecture

## Clean Up (When Done Testing)

To remove all AWS resources:

```bash
cdk destroy
```

**Warning:** This will delete all packages and data permanently!
