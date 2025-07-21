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
    print(f"Public Subnets: {env_config.PUBLIC_SUBNET_CIDRS}")
    print("-" * 50)
    
    try:
        # Create VPC first
        vpc_id = create_vpc(env_config, args.env)
        
        # Create network infrastructure and security group
        network_resources = create_network_infrastructure(env_config, args.env, vpc_id)
        
        print("\n🏁 Network deployment complete!")
        print(f"VPC ID: {vpc_id}")
        print("Subnet IDs:")
        for i, subnet_id in enumerate(network_resources['subnet_ids'], 1):
            print(f"  Subnet {i}: {subnet_id}")
        print(f"IGW ID: {network_resources['igw_id']}")
        print(f"Security Group ID: {network_resources['security_group_id']}")
        
        # Print EC2 deployment commands
        print("\n💡 Next steps:")
        print(f"To deploy Ubuntu server: python scripts/deploy_ec2server1.py -e {args.env}")
        print(f"To deploy Amazon Linux server: python scripts/deploy_ec2server2.py -e {args.env}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()