import json
from scanner import run_scan

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    This is what Lambda calls when the function is triggered
    """
    
    print("Starting AWS Cost Scanner...")
    
    try:
        # Run the scan
        all_findings, total_savings = run_scan()
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Scan completed successfully',
                'findings_count': len(all_findings),
                'total_savings': float(total_savings)
            })
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Scan failed',
                'error': str(e)
            })
        }