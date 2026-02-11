# AWS Cost Optimization Scanner

An automated serverless tool that identifies idle EC2 instances and unattached EBS volumes to prevent cloud waste.

## Problem
Developers often forget to stop EC2 instances or delete unattached EBS volumes, leading to unnecessary AWS charges.

## Solution
A Python-based scanner using Boto3 that:
- Detects unattached EBS volumes
- Identifies idle EC2 instances (< 5% CPU over 7 days)
- Calculates potential monthly savings
- Tracks historical trends in DynamoDB

## Tech Stack
- **Python 3** - Core logic
- **Boto3** - AWS SDK for Python
- **AWS Lambda** - Serverless execution (coming soon)
- **Amazon CloudWatch** - CPU metrics
- **Amazon DynamoDB** - Historical data storage
- **Amazon SES** - Email notifications (coming soon)

## Features
- ✅ Scan for unattached EBS volumes
- ✅ Detect idle EC2 instances using CloudWatch metrics
- ✅ Calculate monthly cost savings
- ✅ Store historical scan data in DynamoDB
- 🚧 Email/Slack notifications (in progress)
- 🚧 Lambda deployment with CloudWatch scheduling (in progress)

## Setup

### Prerequisites
- Python 3.8+
- AWS Account with free tier
- AWS CLI configured

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/aws-cost-scanner.git
cd aws-cost-scanner

# Install dependencies
pip install boto3

# Configure AWS credentials
aws configure
```

### Usage
```bash
python scanner.py
```

## Project Results
In my test environment, the scanner identified:
- 1 unattached EBS volume (8 GB) - **$0.80/month**
- 1 idle EC2 instance (t2.micro) - **$8.35/month**
- **Total potential savings: $9.15/month** ($110/year)

Scaled across a typical dev team with 10-20 resources, this could save **$200+/month**.

## Roadmap
- [ ] HTML email reports with AWS SES
- [ ] Deploy as Lambda function with daily scheduling
- [ ] Add detection for unused Elastic IPs
- [ ] Multi-account support
- [ ] Terraform/CloudFormation for infrastructure-as-code

## What I Learned
- AWS IAM roles and least-privilege security
- CloudWatch metrics and monitoring
- DynamoDB data modeling
- Boto3 API usage and error handling
- Cost optimization strategies

## License
MIT