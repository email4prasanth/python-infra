# ------ File: check_credentials.py ------
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ProfileNotFound

def check_aws_credentials(profile_name):
    try:
        # Create session with specified profile or default
        session = boto3.Session(profile_name=profile_name)
        sts = session.client('sts')
        
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Credentials Valid for profile: '{profile_name or 'default'}'!")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        return True
        
    except ProfileNotFound:
        print(f"❌ Profile '{profile_name}' not found in AWS configuration")
        print("Check your ~/.aws/config and ~/.aws/credentials files")
        return False
    except NoCredentialsError:
        print(f"❌ No AWS credentials found for profile '{profile_name}'")
        print("Configure with: aws configure --profile " + (profile_name or "default"))
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ Credentials error ({error_code}) for profile '{profile_name}': {error_msg}")
        return False

if __name__ == "__main__":
    # Specify the profile name you want to check
    profile_to_check = "tut"
    check_aws_credentials("tut")



# ------ File: config\__init__.py ------
# config/__init__.py
import importlib

def load_config(env):
    """Dynamically load configuration for the specified environment"""
    try:
        module = importlib.import_module(f"config.{env}")
        return module
    except ImportError:
        raise ValueError(f"Invalid environment: {env}. Valid options: dev, prod")



# ------ File: config\dev.py ------
# Development environment configuration
REGION = "us-east-1"
VPC_CIDR = "10.0.0.0/16"
PUBLIC_SUBNET_CIDRS = ["10.0.1.0/24", "10.0.2.0/24"]
AVAILABILITY_ZONES = ["us-east-1a", "us-east-1b"]
PROFILE_NAME = "tut"



# ------ File: config\prod.py ------
# Production environment configuration
REGION = "us-east-1"
VPC_CIDR = "10.1.0.0/16"
PUBLIC_SUBNET_CIDRS = ["10.1.1.0/24", "10.1.2.0/24"]
AVAILABILITY_ZONES = ["us-east-1a", "us-east-1b"]
PROFILE_NAME = "tut"



# ------ File: destroy\__init__.py ------



# ------ File: destroy\destruct_network.py ------
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
        subnet_base_name = f"py-infra-{environment}-public-subnet"
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
            {'Name': 'tag:Project', 'Values': ['py-infra']},
            {'Name': 'tag:Environment', 'Values': [environment]},
            {'Name': 'tag:Name', 'Values': [f"{subnet_base_name}-*"]}
        ])['Subnets']
        
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            subnet_name = next(tag['Value'] for tag in subnet['Tags'] if tag['Key'] == 'Name')
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



# ------ File: destroy\destruct_vpc.py ------
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



# ------ File: infra\__init__.py ------



# ------ File: infra\infra_network.py ------
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



# ------ File: infra\infra_vpc.py ------
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



# ------ File: scripts\deploy_network.py ------
import sys
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
# Add project root to path
from utils.path_utils import setup_paths
setup_paths()

import argparse
from config import load_config
from infra.infra_vpc import create_vpc
from infra.infra_network import create_network_infrastructure

def main():
    parser = argparse.ArgumentParser(description='Deploy AWS network infrastructure')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], default='dev',
                        help='Environment to deploy to (default: dev)')
    args = parser.parse_args()
    
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    print(f"🚀 Deploying network in {args.env.upper()} environment")
    print(f"Region: {env_config.REGION}")
    print(f"VPC CIDR: {env_config.VPC_CIDR}")
    print(f"Public Subnet: {env_config.PUBLIC_SUBNET_CIDRS}")
    print("-" * 50)
    
    try:
        vpc_id = create_vpc(env_config, args.env)
        network_resources = create_network_infrastructure(env_config, args.env, vpc_id)
        print("\n🏁 Network deployment complete!")
        print(f"VPC ID: {vpc_id}")
        print("Subnet IDs:")
        for i, subnet_id in enumerate(network_resources['subnet_ids'], 1):
            print(f"  Subnet {i}: {subnet_id}")
        print(f"IGW ID: {network_resources['igw_id']}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()  



# ------ File: scripts\deploy_vpc.py ------
# Add project root to path
import sys
import os
from pathlib import Path

# Get the current script's directory
current_dir = Path(__file__).resolve().parent
# Get the project root (parent of current_dir)
project_root = current_dir.parent

# Add project root to Python path
sys.path.insert(0, str(project_root))

# Now import utils
from utils.path_utils import setup_paths
setup_paths()

import argparse
from config import load_config
from infra.infra_vpc import create_vpc

def main():
    parser = argparse.ArgumentParser(description='Deploy AWS VPC for py-infra project')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], default='dev',
                        help='Environment to deploy to (default: dev)')
    args = parser.parse_args()
    
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    print(f"🚀 Creating VPC in {args.env.upper()} environment")
    print(f"Region: {env_config.REGION}")
    print(f"CIDR: {env_config.VPC_CIDR}")
    print(f"Profile: {env_config.PROFILE_NAME}")
    print("-" * 50)
    
    try:
        vpc_id = create_vpc(env_config, args.env)
        print(f"\n🏁 VPC creation complete! ID: {vpc_id}")
    except Exception as e:
        print(f"\n❌ VPC creation failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()



# ------ File: scripts\destroy_network.py ------
import sys
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Add project root to path
from utils.path_utils import setup_paths
setup_paths()

import argparse
from config import load_config
from destroy.destruct_network import destroy_network_infrastructure

def main():
    parser = argparse.ArgumentParser(description='Destroy AWS network infrastructure')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], required=True,
                        help='Environment to destroy (required)')
    parser.add_argument('--force', action='store_true',
                        help='Skip confirmation prompt')
    args = parser.parse_args()
    
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    vpc_name = f"py-infra-{args.env}-vpc"
    
    if not args.force:
        confirmation = input(f"Type 'DESTROY {args.env}' to confirm: ")
        if confirmation != f"DESTROY {args.env}":
            print("❌ Destruction cancelled")
            exit(0)
    
    try:
        success = destroy_network_infrastructure(env_config, args.env)
        if success:
            print("\n🗑️ Network destruction complete!")
        else:
            print("\n❌ Network destruction failed")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Destruction failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()



# ------ File: scripts\destroy_vpc.py ------
import sys
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Add project root to path
from utils.path_utils import setup_paths
setup_paths()

import argparse
from config import load_config
from destroy.destruct_vpc import destroy_vpc

def main():
    parser = argparse.ArgumentParser(description='Destroy AWS VPC for py-infra project')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], required=True,
                        help='Environment to destroy (required)')
    parser.add_argument('--force', action='store_true',
                        help='Skip confirmation prompt')
    args = parser.parse_args()
    
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    vpc_name = f"py-infra-{args.env}-vpc"
    
    print(f"⚠️ DESTROYING VPC in {args.env.upper()} environment")
    print(f"VPC Name: {vpc_name}")
    print(f"Region: {env_config.REGION}")
    print(f"Profile: {env_config.PROFILE_NAME}")
    print("-" * 50)
    
    # Confirm destruction
    if not args.force:
        confirmation = input(f"Type '{vpc_name}' to confirm destruction: ")
        if confirmation != vpc_name:
            print("❌ Destruction cancelled")
            exit(0)
    
    # Destroy VPC
    success = destroy_vpc(env_config, args.env)
    
    if success:
        print("\n🗑️ VPC destruction complete!")
    else:
        print("\n❌ VPC destruction failed. See errors above.")
        exit(1)

if __name__ == "__main__":
    main()



# ------ File: utils\__init__.py ------



# ------ File: utils\path_utils.py ------
# utils/path_utils.py
import sys
import os
from pathlib import Path

def setup_paths():
    """Add project root to Python path"""
    # Get the path to the current file
    current_file = Path(__file__).resolve()
    
    # Project root is two levels up from utils directory
    project_root = current_file.parent.parent
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))



