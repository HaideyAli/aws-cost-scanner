import boto3
from datetime import datetime
from decimal import Decimal

ses = boto3.client('ses', region_name='us-east-2')

# DynamoDB client (ADD THIS)
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('CostScannerFindings')

SENDER_EMAIL = "haiderali1248@outlook.com"  
RECIPIENT_EMAIL = "haiderali1248@outlook.com" 

def create_html_email(findings, total_savings, scan_date):
    """Create a high-fidelity formatted HTML email report"""
    
    volumes = [f for f in findings if f['resource_type'] == 'EBS Volume']
    instances = [f for f in findings if f['resource_type'] == 'EC2 Instance']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #16191f;
                background-color: #f2f3f3;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 650px;
                margin: 40px auto;
                background-color: #ffffff;
                border: 1px solid #d5dbdb;
                border-radius: 8px;
                overflow: hidden;
            }}
            .header {{
                background-color: #232f3e;
                padding: 30px;
                text-align: left;
            }}
            .logo-text {{
                color: #ff9900;
                font-size: 24px;
                font-weight: 800;
                letter-spacing: -1px;
            }}
            .header-subtitle {{
                color: #ffffff;
                font-size: 14px;
                margin-top: 5px;
                opacity: 0.8;
            }}
            .content {{
                padding: 30px;
            }}
            .hero-card {{
                background: linear-gradient(135deg, #ff9900 0%, #ffb84d 100%);
                padding: 2px;
                border-radius: 6px;
                margin-bottom: 25px;
            }}
            .hero-inner {{
                background: white;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            }}
            .savings-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: #545b64;
                font-weight: 700;
            }}
            .savings-amount {{
                font-size: 42px;
                font-weight: 800;
                color: #232f3e;
                margin: 5px 0;
            }}
            /* Table-based Grid for Email Compatibility */
            .stats-table {{
                width: 100%;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background-color: #f8f9f9;
                border: 1px solid #e9ebed;
                padding: 20px;
                border-radius: 4px;
                text-align: center;
            }}
            .stat-num {{
                font-size: 28px;
                font-weight: 700;
                color: #ff9900;
            }}
            .stat-label {{
                font-size: 12px;
                color: #545b64;
                font-weight: 600;
            }}
            .section-header {{
                font-size: 18px;
                font-weight: 700;
                border-bottom: 2px solid #eaeded;
                padding-bottom: 8px;
                margin: 30px 0 15px;
                color: #232f3e;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th {{
                text-align: left;
                font-size: 11px;
                text-transform: uppercase;
                color: #545b64;
                padding: 10px;
                background: #fbfbfb;
                border-bottom: 1px solid #eaeded;
            }}
            td {{
                padding: 12px 10px;
                border-bottom: 1px solid #f2f3f3;
                font-size: 13px;
            }}
            .resource-id {{
                font-family: 'Monaco', 'Consolas', monospace;
                color: #0073bb;
                font-size: 12px;
            }}
            .badge {{
                background: #e1eaf3;
                color: #004b73;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            .cost {{
                font-weight: 700;
                color: #d13212;
            }}
            .alert-box {{
                background-color: #fff9e6;
                border-left: 4px solid #ff9900;
                padding: 15px;
                margin-top: 25px;
            }}
            .footer {{
                background-color: #f2f3f3;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #545b64;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-text">AWS <span style="color:white; font-weight:300;">CostScanner</span></div>
                <div class="header-subtitle">Optimization Report for {scan_date}</div>
            </div>
            
            <div class="content">
                <div class="hero-card">
                    <div class="hero-inner">
                        <div class="savings-label">Est. Monthly Savings Potential</div>
                        <div class="savings-amount">${float(total_savings):.2f}</div>
                    </div>
                </div>

                <table class="stats-table">
                    <tr>
                        <td width="50%" style="padding-right:10px;">
                            <div class="stat-card">
                                <div class="stat-num">{len(volumes)}</div>
                                <div class="stat-label">Stale Volumes</div>
                            </div>
                        </td>
                        <td width="50%" style="padding-left:10px;">
                            <div class="stat-card">
                                <div class="stat-num">{len(instances)}</div>
                                <div class="stat-label">Idle Instances</div>
                            </div>
                        </td>
                    </tr>
                </table>
    """

    if volumes:
        html += """<div class="section-header">Unattached EBS Volumes</div>
                   <table><tr><th>Volume ID</th><th>Size</th><th>Monthly Waste</th></tr>"""
        for vol in volumes:
            html += f"""
                <tr>
                    <td><span class="resource-id">{vol['resource_id']}</span><br><span class="badge">{vol['volume_type']}</span></td>
                    <td>{vol['size_gb']} GB</td>
                    <td class="cost">${float(vol['monthly_cost']):.2f}</td>
                </tr>"""
        html += "</table>"

    if instances:
        html += """<div class="section-header">Idle EC2 Instances</div>
                   <table><tr><th>Instance / ID</th><th>CPU %</th><th>Monthly Waste</th></tr>"""
        for inst in instances:
            html += f"""
                <tr>
                    <td><strong>{inst['name']}</strong><br><span class="resource-id">{inst['resource_id']}</span></td>
                    <td><span class="badge">{float(inst['avg_cpu_percent']):.1f}%</span></td>
                    <td class="cost">${float(inst['monthly_cost']):.2f}</td>
                </tr>"""
        html += "</table>"

    # Add trend analysis (simple version)
    yesterday = get_yesterday_savings()
    
    if yesterday is not None:
        change = total_savings - yesterday
        change_percent = (change / yesterday * 100) if yesterday > 0 else 0
        
        # Color: green if improved (decreased), red if worse (increased)
        trend_color = "#1d8102" if change < 0 else "#d13212"
        trend_arrow = "↓" if change < 0 else "↑"
        trend_word = "Improved" if change < 0 else "Increased"
        
        html += f"""
        <div style="background-color: #f7f8f9; border-left: 4px solid {trend_color}; 
                    padding: 20px 25px; margin: 30px 0; border-radius: 2px;">
            <h3 style="margin: 0 0 10px 0; color: #232f3e;">📊 Day-Over-Day Trend</h3>
            <p style="margin: 5px 0; color: #16191f;">
                <strong>Yesterday:</strong> ${yesterday:.2f}/month
            </p>
            <p style="margin: 5px 0; color: #16191f;">
                <strong>Today:</strong> ${float(total_savings):.2f}/month
            </p>
            <p style="margin: 5px 0; color: {trend_color}; font-weight: 700; font-size: 16px;">
                {trend_arrow} {trend_word} by ${abs(change):.2f} ({abs(change_percent):.1f}%)
            </p>
        </div>
        """

    if not volumes and not instances:
        html += """<div style="text-align:center; padding: 40px 0;">
                    <div style="font-size: 40px;">✅</div>
                    <div style="font-weight:700; color:#1d8102;">Everything looks optimized!</div>
                   </div>"""
    else:
        html += """
            <div class="alert-box">
                <strong style="color: #232f3e;">Recommended Actions:</strong>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 13px;">
                    <li>Snapshot and delete unattached volumes.</li>
                    <li>Rightsizing or stopping idle EC2 instances.</li>
                </ul>
            </div>"""

    html += f"""
            </div>
            <div class="footer">
                <p>This report was generated automatically by <strong>AWS CostScanner</strong>.</p>
                <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>"""
    
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

def get_yesterday_savings():
    """Get yesterday's savings for comparison"""
    try:
        response = table.scan()
        items = response['Items']
        
        if len(items) < 2:
            return None  # Not enough history yet
        
        # Sort by date
        items.sort(key=lambda x: x['scan_date'], reverse=True)
        
        # Return yesterday's (second most recent) savings
        return float(items[1]['total_monthly_savings'])
        
    except Exception as e:
        print(f"Could not get historical data: {e}")
        return None

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