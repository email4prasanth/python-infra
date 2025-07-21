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