import boto3
from datetime import datetime
from decimal import Decimal

ses = boto3.client('ses', region_name='us-east-2')

SENDER_EMAIL = "haiderali1248@outlook.com"  
RECIPIENT_EMAIL = "haiderali1248@outlook.com" 

def create_html_email(findings, total_savings, scan_date):
    """Create formatted HTML email report"""
    
    # Separate findings by type
    volumes = [f for f in findings if f['resource_type'] == 'EBS Volume']
    instances = [f for f in findings if f['resource_type'] == 'EC2 Instance']
    
    # Build HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #232F3E;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .summary {{
                background-color: #FF9900;
                color: white;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                text-align: center;
            }}
            .summary h2 {{
                margin: 0;
                font-size: 32px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #232F3E;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .warning {{
                color: #D13212;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 30px;
                padding: 20px;
                background-color: #f5f5f5;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AWS Cost Scanner Report</h1>
            <p>Daily Cloud Waste Detection</p>
        </div>
        
        <div class="summary">
            <p>Total Monthly Savings Potential</p>
            <h2>${float(total_savings):.2f}</h2>
            <p>Scan Date: {scan_date}</p>
        </div>
        
        <h2>Summary</h2>
        <p>Found <strong>{len(findings)}</strong> resources that could be optimized:</p>
        <ul>
            <li>Unattached EBS Volumes: <strong>{len(volumes)}</strong></li>
            <li>Idle EC2 Instances: <strong>{len(instances)}</strong></li>
        </ul>
    """
    
    # Add EBS volumes table if any found
    if volumes:
        html += """
        <h2>Unattached EBS Volumes</h2>
        <table>
            <tr>
                <th>Volume ID</th>
                <th>Size (GB)</th>
                <th>Type</th>
                <th>Monthly Cost</th>
            </tr>
        """
        for vol in volumes:
            html += f"""
            <tr>
                <td>{vol['resource_id']}</td>
                <td>{vol['size_gb']}</td>
                <td>{vol['volume_type']}</td>
                <td class="warning">${float(vol['monthly_cost']):.2f}</td>
            </tr>
            """
        html += "</table>"
    
    # Add EC2 instances table if any found
    if instances:
        html += """
        <h2>Idle EC2 Instances</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Instance ID</th>
                <th>Type</th>
                <th>Avg CPU %</th>
                <th>Monthly Cost</th>
            </tr>
        """
        for inst in instances:
            html += f"""
            <tr>
                <td>{inst['name']}</td>
                <td>{inst['resource_id']}</td>
                <td>{inst['instance_type']}</td>
                <td>{float(inst['avg_cpu_percent']):.1f}%</td>
                <td class="warning">${float(inst['monthly_cost']):.2f}</td>
            </tr>
            """
        html += "</table>"
    
    # Recommendations
    html += """
        <h2>Recommended Actions</h2>
        <ul>
            <li><strong>Unattached EBS Volumes:</strong> Review and delete volumes that are no longer needed. Create snapshots first if you need backups.</li>
            <li><strong>Idle EC2 Instances:</strong> Stop instances when not in use, or consider downsizing to smaller instance types.</li>
        </ul>
        
        <div class="footer">
            <p>This is an automated report from AWS Cost Scanner</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email(findings, total_savings):
    """Send email report via AWS SES"""
    
    scan_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create HTML content
    html_body = create_html_email(findings, total_savings, scan_date)
    
    # Create plain text version (fallback)
    text_body = f"""
AWS Cost Scanner Report - {scan_date}

Total Monthly Savings Potential: ${float(total_savings):.2f}

Found {len(findings)} resources that could be optimized.

For full details, please view the HTML version of this email.
    """
    
    # Email subject
    subject = f"AWS Cost Report: ${float(total_savings):.2f}/month savings found - {scan_date}"
    
    try:
        response = ses.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [RECIPIENT_EMAIL]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text_body,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"  SUCCESS: Email sent! Message ID: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"  ERROR: Could not send email: {e}")
        return False


# Test function
if __name__ == "__main__":
    # Test data
    test_findings = [
        {
            'resource_type': 'EBS Volume',
            'resource_id': 'vol-0f5f53ca9617302f8',
            'size_gb': 8,
            'volume_type': 'gp3',
            'monthly_cost': 0.80
        },
        {
            'resource_type': 'EC2 Instance',
            'resource_id': 'i-0f24cb36b4bd18a3b',
            'name': 'test-instance-for-scanner',
            'instance_type': 't2.micro',
            'avg_cpu_percent': 0.3,
            'monthly_cost': 7.49
        }
    ]
    
    send_email(test_findings, 8.29)