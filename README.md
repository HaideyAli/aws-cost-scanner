# AWS Cost Optimization Scanner

Automated serverless tool that identifies idle EC2 instances and unattached EBS volumes to prevent cloud waste.

## Problem
Developers often forget to stop EC2 instances or delete unattached EBS volumes, leading to unnecessary AWS charges that can exceed $200/month in typical dev environments.

## Solution
A Python-based scanner using Boto3 that:
- Detects unattached EBS volumes
- Identifies idle EC2 instances (< 5% CPU over 7 days)
- Calculates potential monthly savings
- Sends formatted HTML email reports
- Runs automatically via Lambda on a daily schedule
- Tracks historical trends in DynamoDB

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    EventBridge (CloudWatch Events)          │
│                    Triggers: Daily at 9 AM UTC              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS Lambda Function                      │
│                    (scanner code runs here)                 │
└─────┬──────────┬──────────┬──────────┬──────────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
   ┌────┐    ┌────────┐ ┌────────┐ ┌─────┐
   │EC2 │    │CloudW. │ │DynamoDB│ │ SES │
   │API │    │Metrics │ │Storage │ │Email│
   └────┘    └────────┘ └────────┘ └─────┘
```

## Tech Stack
- **Python 3.12** - Core logic
- **Boto3** - AWS SDK for Python
- **AWS Lambda** - Serverless execution
- **Amazon EC2** - Resource scanning
- **Amazon CloudWatch** - CPU metrics analysis
- **Amazon DynamoDB** - Historical data storage
- **Amazon SES** - HTML email notifications
- **Amazon EventBridge** - Daily scheduling
- **IAM** - Least-privilege security

## Features
- ✅ Scan for unattached EBS volumes
- ✅ Detect idle EC2 instances using CloudWatch metrics
- ✅ Calculate monthly cost savings
- ✅ Send formatted HTML email reports
- ✅ Store historical scan data in DynamoDB
- ✅ Automated daily execution via Lambda
- ✅ Serverless architecture (no infrastructure management)

## Setup

### Prerequisites
- Python 3.8+
- AWS Account with free tier
- AWS CLI configured

### Local Testing
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/aws-cost-scanner.git
cd aws-cost-scanner

# Install dependencies
pip install boto3

# Configure AWS credentials
aws configure

# Run scanner locally
python scanner.py
```

### Lambda Deployment

1. **Create IAM role** with permissions:
   - EC2ReadOnly
   - CloudWatchReadOnly
   - DynamoDBFullAccess
   - SESFullAccess

2. **Verify email in SES:**
```bash
   aws ses verify-email-identity --email-address your@email.com --region us-east-2
```

3. **Create DynamoDB table:**
```bash
   aws dynamodb create-table \
     --table-name CostScannerFindings \
     --attribute-definitions AttributeName=scan_date,AttributeType=S \
     --key-schema AttributeName=scan_date,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-2
```

4. **Package and deploy:**
```bash
   zip -r lambda_deployment.zip scanner.py email_notifier.py lambda_function.py
   aws lambda create-function \
     --function-name CostScanner \
     --runtime python3.12 \
     --role arn:aws:iam::YOUR-ACCOUNT-ID:role/CostScannerLambdaRole \
     --handler lambda_function.lambda_handler \
     --zip-file fileb://lambda_deployment.zip \
     --timeout 60 \
     --region us-east-2
```

5. **Set up daily schedule:**
```bash
   aws events put-rule \
     --name DailyCostScan \
     --schedule-expression "cron(0 9 * * ? *)" \
     --region us-east-2
   
   aws lambda add-permission \
     --function-name CostScanner \
     --statement-id AllowEventBridge \
     --action lambda:InvokeFunction \
     --principal events.amazonaws.com \
     --region us-east-2
```

## Project Results

### Test Environment
In my free-tier test environment, the scanner identified:
- 1 unattached EBS volume (8 GB) - **$0.80/month**
- 1 idle EC2 instance (t2.micro) - **$7.49/month**
- **Total: $8.29/month** ($99/year)

### Mock Production Scenario
Simulated 10-person dev team environment ([see details](MOCK_SCENARIO.md)):
- 10 idle EC2 instances - **$247.80/month**
- 25 unattached EBS volumes (1,540 GB) - **$114.00/month**
- **Total potential savings: $361.80/month** ($4,342/year)

### Enterprise Extrapolation
50-developer organization with 5 teams:
- **Estimated savings: $1,809/month** ($21,708/year)

## Sample Email Report

The scanner sends daily HTML email reports with:
- Total monthly savings summary
- Table of unattached EBS volumes with sizes and costs
- Table of idle EC2 instances with CPU metrics
- Recommended actions for each finding

## What I Learned
- AWS IAM roles and least-privilege security principles
- CloudWatch metrics collection and analysis
- DynamoDB data modeling for time-series data
- Boto3 API usage and error handling
- AWS SES email formatting and delivery
- Lambda function deployment and scheduling
- Serverless architecture patterns
- Cost optimization strategies for cloud infrastructure

## Future Enhancements
- [ ] Multi-region support
- [ ] Slack webhook integration
- [ ] Detection for unused Elastic IPs
- [ ] RDS idle instance detection
- [ ] Auto-remediation (with approval workflow)
- [ ] Cost forecasting with trend analysis
- [ ] Terraform/CloudFormation IaC deployment

## License
MIT