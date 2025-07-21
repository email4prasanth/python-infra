import sys
import os
import boto3
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from utils.path_utils import setup_paths
from utils.aws_utils import get_network_resources
setup_paths()

import argparse
from config import load_config
from infra.infra_ec2server2 import create_ec2_server2

def main():
    parser = argparse.ArgumentParser(description='Deploy AWS EC2 Server2 (Amazon Linux)')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], required=True,
                        help='Environment to deploy to')
    
    args = parser.parse_args()
    
    try:
        # Load environment configuration
        env_config = load_config(args.env)
        
        # Create AWS session
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        
        # Get network resources automatically
        _, _, subnet_id, sg_id = get_network_resources(
            session, args.env, env_config.REGION
        )
        
        print(f"🔍 Using Subnet 2: {subnet_id}")
        print(f"🔍 Using Security Group: {sg_id}")
        
        # Create server
        instance_id = create_ec2_server2(
            env_config, 
            args.env, 
            subnet_id, 
            sg_id
        )
        
        print(f"\n🏁 EC2 Server2 (Amazon Linux) created! ID: {instance_id}")
        print("Note: It may take a few minutes for the instance to be fully operational")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()