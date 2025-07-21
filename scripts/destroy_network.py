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