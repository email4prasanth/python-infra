# destroy/vpc.py
import boto3
import time
from botocore.exceptions import ClientError

def destroy_vpc(env_config, environment):
    """
    Destroys the VPC for the specified environment
    """
    try:
        # Create session with specified profile
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        # Generate VPC name dynamically
        vpc_name = f"py-infra-{environment}-vpc"
        
        # Find VPC by name tag
        response = ec2.describe_vpcs(Filters=[
            {'Name': 'tag:Name', 'Values': [vpc_name]},
            {'Name': 'tag:Project', 'Values': ['py-infra']},
            {'Name': 'tag:Environment', 'Values': [environment]}
        ])
        
        if not response['Vpcs']:
            print(f"❌ VPC not found: {vpc_name}")
            return False
            
        vpc_id = response['Vpcs'][0]['VpcId']
        print(f"🔍 Found VPC: {vpc_name} ({vpc_id})")
        
        # Delete the VPC
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"🗑️ VPC deletion initiated: {vpc_name}")
        
        # Wait for VPC to be deleted
        print("⏳ Waiting for VPC to be deleted...", end='', flush=True)
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while time.time() - start_time < timeout:
            try:
                ec2.describe_vpcs(VpcIds=[vpc_id])
                # Still exists, wait and check again
                print('.', end='', flush=True)
                time.sleep(5)
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVpcID.NotFound':
                    print("\n✅ VPC deleted successfully")
                    return True
                # Other errors should be raised
                raise
        
        print("\n❌ Timeout waiting for VPC deletion")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        if error_code == 'InvalidVpcID.NotFound':
            print(f"✅ VPC already deleted: {vpc_name}")
            return True
            
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False