"""
Complete Infrastructure Deployment Script
Creates VPC and all network components
"""

import argparse
from config import load_config
from infra_vpc import create_vpc
from infra_network import create_network_infrastructure

def main():
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description='Deploy complete AWS infrastructure for py-infra project')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], default='dev',
                        help='Environment to deploy to (default: dev)')
    parser.add_argument('--skip-network', action='store_true',
                        help='Skip network infrastructure creation (VPC only)')
    args = parser.parse_args()
    
    # Load environment-specific configuration
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    print(f"🚀 Deploying infrastructure in {args.env.upper()} environment")
    print("Configuration:")
    print(f"  Region: {env_config.REGION}")
    print(f"  VPC CIDR: {env_config.VPC_CIDR}")
    
    if not args.skip_network:
        print(f"  Public Subnet CIDR: {env_config.PUBLIC_SUBNET_CIDR}")
        print(f"  Availability Zone: {env_config.AVAILABILITY_ZONE}")
    
    print(f"  AWS Profile: {env_config.PROFILE_NAME}")
    print("-" * 50)
    
    try:
        # Create VPC
        print("🔨 Creating VPC...")
        vpc_id = create_vpc(env_config, args.env)
        print(f"✅ VPC created: {vpc_id}")
        
        if args.skip_network:
            print("\n🏁 VPC-only deployment complete!")
            return
        
        # Create network infrastructure
        print("\n🔨 Creating network infrastructure...")
        network_resources = create_network_infrastructure(env_config, args.env, vpc_id)
        
        print("\n🏁 Infrastructure deployment complete!")
        print("Created resources:")
        print(f"  VPC ID: {vpc_id}")
        print(f"  Public Subnet ID: {network_resources['subnet_id']}")
        print(f"  Internet Gateway ID: {network_resources['igw_id']}")
        print(f"  Route Table ID: {network_resources['route_table_id']}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()