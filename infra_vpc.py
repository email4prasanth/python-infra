import boto3
from botocore.exceptions import ClientError

def create_vpc(env_config, environment):
    """
    Creates a VPC with the specified configuration
    Generates VPC name dynamically based on environment
    """
    try:
        # Create session with specified profile
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        # Generate VPC name dynamically
        vpc_name = f"py-infra-{environment}-vpc"
        
        # Create VPC
        vpc_response = ec2.create_vpc(
            CidrBlock=env_config.VPC_CIDR,
            AmazonProvidedIpv6CidrBlock=False,
            InstanceTenancy='default'
        )
        vpc_id = vpc_response['Vpc']['VpcId']
        
        # Add name and environment tags to VPC
        ec2.create_tags(
            Resources=[vpc_id],
            Tags=[
                {'Key': 'Name', 'Value': vpc_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        
        # Enable DNS support and hostnames
        ec2.modify_vpc_attribute(
            VpcId=vpc_id,
            EnableDnsSupport={'Value': True}
        )
        ec2.modify_vpc_attribute(
            VpcId=vpc_id,
            EnableDnsHostnames={'Value': True}
        )
        
        print(f"✅ VPC created successfully: {vpc_name} ({vpc_id})")
        return vpc_id
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise