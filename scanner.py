import boto3
from datetime import datetime, timedelta
import json
from decimal import Decimal

# AWS clients
ec2 = boto3.client('ec2', region_name='us-east-2')
cloudwatch = boto3.client('cloudwatch', region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('CostScannerFindings')

# Pricing dictionary
PRICING = {
    'ebs_gb_month': 0.10,
    'ec2': {
        't2.micro': 0.0116,    
        't2.small': 0.023,
        't2.medium': 0.0464,
        't3.micro': 0.0104,
        't3.small': 0.0208,
        't3.medium': 0.0416,
    }
}

def find_unattached_volumes():
    """Find all unattached EBS volumes"""
    print("\nScanning for unattached EBS volumes...")
    
    volumes = ec2.describe_volumes(
        Filters=[
            {'Name': 'status', 'Values': ['available']}
        ]
    )
    
    findings = []
    total_waste = 0
    
    for volume in volumes['Volumes']:
        volume_id = volume['VolumeId']
        size_gb = volume['Size']
        volume_type = volume['VolumeType']
        created = volume['CreateTime']
        
        # Calculate monthly cost
        monthly_cost = size_gb * PRICING['ebs_gb_month']
        total_waste += monthly_cost
        
        findings.append({
            'resource_type': 'EBS Volume',
            'resource_id': volume_id,
            'size_gb': size_gb,
            'volume_type': volume_type,
            'created': str(created),
            'monthly_cost': float(round(monthly_cost, 2))
        })
        
        print(f"  WARNING: Found unattached volume: {volume_id} ({size_gb} GB) - ${monthly_cost:.2f}/month")
    
    if not findings:
        print("  OK: No unattached volumes found")
    
    return findings, total_waste


def get_average_cpu(instance_id):
    """Get average CPU utilization over the last 7 days"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            total = sum(point['Average'] for point in response['Datapoints'])
            avg = total / len(response['Datapoints'])
            return avg
        else:
            return 0.0
            
    except Exception as e:
        print(f"    Warning: Could not get CPU metrics: {e}")
        return 0.0


def find_idle_instances():
    """Find EC2 instances with low CPU usage"""
    print("\nScanning for idle EC2 instances...")
    
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    findings = []
    total_waste = 0
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            
            # Get name tag
            name = 'No name'
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
            
            print(f"  Checking: {name} ({instance_id})...")
            
            # Get CPU metrics
            cpu_avg = get_average_cpu(instance_id)
            
            # Consider idle if CPU < 5%
            if cpu_avg < 5.0:
                hourly_cost = PRICING['ec2'].get(instance_type, 0.05)
                monthly_cost = hourly_cost * 24 * 30
                total_waste += monthly_cost
                
                findings.append({
                    'resource_type': 'EC2 Instance',
                    'resource_id': instance_id,
                    'name': name,
                    'instance_type': instance_type,
                    'avg_cpu_percent': float(round(cpu_avg, 2)),
                    'monthly_cost': float(round(monthly_cost, 2))
                })
                
                print(f"  WARNING: IDLE instance: {name} - {cpu_avg:.1f}% CPU - ${monthly_cost:.2f}/month")
            else:
                print(f"  OK: Active instance - {cpu_avg:.1f}% CPU")
    
    if not findings:
        print("  OK: No idle instances found")
    
    return findings, total_waste


def save_to_dynamodb(all_findings, total_savings):
    """Save scan results to DynamoDB"""
    print("\nSaving results to DynamoDB...")
    
    scan_date = datetime.now().strftime('%Y-%m-%d')
    
    item = {
        'scan_date': scan_date,
        'findings': all_findings,
        'total_monthly_savings': Decimal(str(round(total_savings, 2))),
        'scan_timestamp': datetime.now().isoformat()
    }
    
    try:
        table.put_item(Item=item)
        print(f"  SUCCESS: Saved scan results for {scan_date}")
        return True
    except Exception as e:
        print(f"  ERROR: Could not save to DynamoDB: {e}")
        return False


def get_historical_savings():
    """Retrieve historical savings from DynamoDB"""
    print("\nRetrieving historical data...")
    
    try:
        response = table.scan()
        items = response['Items']
        
        if not items:
            print("  No historical data yet")
            return []
        
        items.sort(key=lambda x: x['scan_date'], reverse=True)
        
        print(f"  Found {len(items)} previous scans")
        
        for item in items[:7]:
            savings = float(item['total_monthly_savings'])
            print(f"  {item['scan_date']}: ${savings:.2f}/month potential savings")
        
        return items
        
    except Exception as e:
        print(f"  ERROR: Could not retrieve historical data: {e}")
        return []


def run_scan():
    """Main function to run the complete scan"""
    print("=" * 60)
    print("AWS COST SCANNER - Running Daily Scan")
    print("=" * 60)
    
    # Find waste
    volume_findings, volume_waste = find_unattached_volumes()
    instance_findings, instance_waste = find_idle_instances()
    
    # Combine results
    all_findings = volume_findings + instance_findings
    total_savings = volume_waste + instance_waste
    
    # Print summary
    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Unattached EBS Volumes: {len(volume_findings)}")
    print(f"Idle EC2 Instances: {len(instance_findings)}")
    print(f"Total Monthly Savings Potential: ${total_savings:.2f}")
    print("=" * 60)
    
    # Save to DynamoDB
    save_to_dynamodb(all_findings, total_savings)
    
    # Show historical trend
    get_historical_savings()
    
    return all_findings, total_savings


if __name__ == "__main__":
    run_scan()