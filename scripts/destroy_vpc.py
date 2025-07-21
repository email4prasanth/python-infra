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