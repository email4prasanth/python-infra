"""
Network Infrastructure Destruction
Destroys resources in reverse order of creation:
1. Route Table
2. Internet Gateway
3. Subnet
4. VPC
"""

import boto3
import time
from botocore.exceptions import ClientError

def destroy_network_infrastructure(env_config, environment):
    """
    Destroys network infrastructure and VPC for the specified environment
    """
    try:
        # Create session with specified profile
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        # Generate resource names dynamically
        vpc_name = f"py-infra-{environment}-vpc"
        subnet_name = f"py-infra-{environment}-public-subnet"
        igw_name = f"py-infra-{environment}-igw"
        rt_name = f"py-infra-{environment}-public-rt"
        
        # Find VPC by name tag
        vpcs = ec2.describe_vpcs(Filters=[
            {'Name': 'tag:Name', 'Values': [vpc_name]},
            {'Name': 'tag:Project', 'Values': ['py-infra']},
            {'Name': 'tag:Environment', 'Values': [environment]}
        ])['Vpcs']
        
        if not vpcs:
            print(f"❌ VPC not found: {vpc_name}")
            return False
        
        vpc_id = vpcs[0]['VpcId']
        print(f"🔍 Found VPC: {vpc_name} ({vpc_id})")
        
        # 1. Find and delete route tables
        route_tables = ec2.describe_route_tables(Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'tag:Name', 'Values': [rt_name]},
            {'Name': 'tag:Project', 'Values': ['py-infra']}
        ])['RouteTables']
        
        for rt in route_tables:
            rt_id = rt['RouteTableId']
            
            # Disassociate all associations
            for assoc in rt['Associations']:
                if not assoc['Main']:  # Skip main route table
                    ec2.disassociate_route_table(AssociationId=assoc['RouteTableAssociationId'])
                    print(f"  - Disassociated route table: {assoc['RouteTableAssociationId']}")
            
            # Delete route table
            ec2.delete_route_table(RouteTableId=rt_id)
            print(f"✅ Deleted route table: {rt_name} ({rt_id})")
        
        # 2. Find and delete internet gateway
        igws = ec2.describe_internet_gateways(Filters=[
            {'Name': 'attachment.vpc-id', 'Values': [vpc_id]},
            {'Name': 'tag:Name', 'Values': [igw_name]},
            {'Name': 'tag:Project', 'Values': ['py-infra']}
        ])['InternetGateways']
        
        for igw in igws:
            igw_id = igw['InternetGatewayId']
            
            # Detach from VPC
            ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            
            # Delete IGW
            ec2.delete_internet_gateway(InternetGatewayId=igw_id)
            print(f"✅ Deleted internet gateway: {igw_name} ({igw_id})")
        
        # 3. Find and delete subnets
        subnets = ec2.describe_subnets(Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'tag:Name', 'Values': [subnet_name]},
            {'Name': 'tag:Project', 'Values': ['py-infra']}
        ])['Subnets']
        
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            ec2.delete_subnet(SubnetId=subnet_id)
            print(f"✅ Deleted subnet: {subnet_name} ({subnet_id})")
        
        # 4. Delete VPC
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"🗑️ VPC deletion initiated: {vpc_name}")
        
        # Wait for VPC deletion
        print("⏳ Waiting for VPC to be deleted...", end='', flush=True)
        start_time = time.time()
        timeout = 300  # 5 minutes
        
        while time.time() - start_time < timeout:
            try:
                ec2.describe_vpcs(VpcIds=[vpc_id])
                print('.', end='', flush=True)
                time.sleep(5)
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVpcID.NotFound':
                    print("\n✅ VPC deleted successfully")
                    return True
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