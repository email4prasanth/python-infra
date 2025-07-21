"""
Network Infrastructure Creation
- Public Subnet
- Internet Gateway (IGW)
- Route Table with public routes
"""

import boto3
from botocore.exceptions import ClientError

def create_network_infrastructure(env_config, environment, vpc_id):
    """
    Creates network infrastructure components in the specified VPC
    Returns dictionary of created resource IDs
    """
    try:
        # Create session with specified profile
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        # Generate resource names dynamically
        subnet_name = f"py-infra-{environment}-public-subnet"
        igw_name = f"py-infra-{environment}-igw"
        rt_name = f"py-infra-{environment}-public-rt"
        
        # 1. Create public subnet
        subnet = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=env_config.PUBLIC_SUBNET_CIDR,
            AvailabilityZone=env_config.AVAILABILITY_ZONE
        )
        subnet_id = subnet['Subnet']['SubnetId']
        
        # Enable auto-assign public IP for the subnet
        ec2.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )
        
        # Tag the subnet
        ec2.create_tags(
            Resources=[subnet_id],
            Tags=[
                {'Key': 'Name', 'Value': subnet_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        print(f"✅ Public subnet created: {subnet_name} ({subnet_id})")
        
        # 2. Create internet gateway (IGW)
        igw = ec2.create_internet_gateway()
        igw_id = igw['InternetGateway']['InternetGatewayId']
        
        # Attach IGW to VPC
        ec2.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )
        
        # Tag the IGW
        ec2.create_tags(
            Resources=[igw_id],
            Tags=[
                {'Key': 'Name', 'Value': igw_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        print(f"✅ Internet Gateway created and attached: {igw_name} ({igw_id})")
        
        # 3. Create and configure route table
        rt = ec2.create_route_table(VpcId=vpc_id)
        rt_id = rt['RouteTable']['RouteTableId']
        
        # Create default route to IGW
        ec2.create_route(
            RouteTableId=rt_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        
        # Associate route table with public subnet
        association = ec2.associate_route_table(
            RouteTableId=rt_id,
            SubnetId=subnet_id
        )
        association_id = association['AssociationId']
        
        # Tag the route table
        ec2.create_tags(
            Resources=[rt_id],
            Tags=[
                {'Key': 'Name', 'Value': rt_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        
        print(f"✅ Route table created and configured: {rt_name} ({rt_id})")
        
        return {
            'subnet_id': subnet_id,
            'igw_id': igw_id,
            'route_table_id': rt_id,
            'association_id': association_id
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise