"""
Network Infrastructure Creation
- Public Subnet-2
- Internet Gateway (IGW)
- Route Table with public routes
"""

import boto3
from botocore.exceptions import ClientError

def create_network_infrastructure(env_config, environment, vpc_id):
    try:
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        # Generate resource names
        igw_name = f"py-infra-{environment}-igw"
        rt_name = f"py-infra-{environment}-public-rt"
        
        subnet_ids = []
        
        # Create internet gateway
        igw = ec2.create_internet_gateway()
        igw_id = igw['InternetGateway']['InternetGatewayId']
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.create_tags(
            Resources=[igw_id],
            Tags=[
                {'Key': 'Name', 'Value': igw_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        print(f"✅ Internet Gateway created and attached: {igw_name} ({igw_id})")
        
        # Create route table
        rt = ec2.create_route_table(VpcId=vpc_id)
        rt_id = rt['RouteTable']['RouteTableId']
        ec2.create_route(
            RouteTableId=rt_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        ec2.create_tags(
            Resources=[rt_id],
            Tags=[
                {'Key': 'Name', 'Value': rt_name},
                {'Key': 'Environment', 'Value': environment},
                {'Key': 'Project', 'Value': 'py-infra'}
            ]
        )
        print(f"✅ Route table created: {rt_name} ({rt_id})")
        
        # Create two public subnets
        for i, (cidr, az) in enumerate(zip(env_config.PUBLIC_SUBNET_CIDRS, env_config.AVAILABILITY_ZONES), 1):
            subnet_name = f"py-infra-{environment}-public-subnet-{i}"
            
            subnet = ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=cidr,
                AvailabilityZone=az
            )
            subnet_id = subnet['Subnet']['SubnetId']
            
            ec2.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )
            
            ec2.create_tags(
                Resources=[subnet_id],
                Tags=[
                    {'Key': 'Name', 'Value': subnet_name},
                    {'Key': 'Environment', 'Value': environment},
                    {'Key': 'Project', 'Value': 'py-infra'}
                ]
            )
            print(f"✅ Public subnet created: {subnet_name} ({subnet_id})")
            
            # Associate subnet with route table
            association = ec2.associate_route_table(
                RouteTableId=rt_id,
                SubnetId=subnet_id
            )
            print(f"  ↳ Associated with route table: {rt_name}")
            
            subnet_ids.append(subnet_id)
        
        return {
            'subnet_ids': subnet_ids,
            'igw_id': igw_id,
            'route_table_id': rt_id
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise