import boto3
from botocore.exceptions import ClientError

def get_network_resources(session, environment, region):
    """
    Fetch network resources for the specified environment
    Returns: (vpc_id, subnet1_id, subnet2_id, sg_id)
    """
    ec2 = session.client('ec2', region_name=region)
    
    # Define resource names
    vpc_name = f"py-infra-{environment}-vpc"
    subnet1_name = f"py-infra-{environment}-public-subnet-1"
    subnet2_name = f"py-infra-{environment}-public-subnet-2"
    sg_name = f"py-infra-{environment}-sg"
    
    # Find VPC
    vpcs = ec2.describe_vpcs(Filters=[
        {'Name': 'tag:Name', 'Values': [vpc_name]},
        {'Name': 'tag:Project', 'Values': ['py-infra']}
    ])['Vpcs']
    
    if not vpcs:
        raise ValueError(f"VPC not found: {vpc_name}")
    
    vpc_id = vpcs[0]['VpcId']
    
    # Find Subnet 1
    subnet1 = ec2.describe_subnets(Filters=[
        {'Name': 'tag:Name', 'Values': [subnet1_name]},
        {'Name': 'vpc-id', 'Values': [vpc_id]}
    ])['Subnets']
    
    if not subnet1:
        raise ValueError(f"Subnet 1 not found: {subnet1_name}")
    subnet1_id = subnet1[0]['SubnetId']
    
    # Find Subnet 2
    subnet2 = ec2.describe_subnets(Filters=[
        {'Name': 'tag:Name', 'Values': [subnet2_name]},
        {'Name': 'vpc-id', 'Values': [vpc_id]}
    ])['Subnets']
    
    if not subnet2:
        raise ValueError(f"Subnet 2 not found: {subnet2_name}")
    subnet2_id = subnet2[0]['SubnetId']
    
    # Find Security Group
    sgs = ec2.describe_security_groups(Filters=[
        {'Name': 'tag:Name', 'Values': [sg_name]},
        {'Name': 'vpc-id', 'Values': [vpc_id]}
    ])['SecurityGroups']
    
    if not sgs:
        raise ValueError(f"Security Group not found: {sg_name}")
    sg_id = sgs[0]['GroupId']
    
    return vpc_id, subnet1_id, subnet2_id, sg_id