import sys
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from utils.path_utils import setup_paths
setup_paths()

import argparse
from config import load_config
from destroy.destruct_ec2server2 import destroy_ec2_server2

def main():
    parser = argparse.ArgumentParser(description='Destroy AWS EC2 Server2 (Amazon Linux)')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], required=True,
                        help='Environment to destroy')
    
    args = parser.parse_args()
    
    print(f"⚠️ DESTROYING EC2 Server2 (Amazon Linux) in {args.env.upper()} environment")
    
    try:
        env_config = load_config(args.env)
        success = destroy_ec2_server2(env_config, args.env)
        if success:
            print("\n🗑️ Server2 destruction complete!")
        else:
            print("\n❌ Destruction failed")
            exit(1)
    except Exception as e:
        print(f"\n❌ Destruction failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()