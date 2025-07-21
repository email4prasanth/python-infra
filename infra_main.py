import argparse
from config import load_config
from infra_vpc import create_vpc

def main():
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description='Create AWS VPC for py-infra project')
    parser.add_argument('-e', '--env', choices=['dev', 'prod'], default='dev',
                        help='Environment to deploy to (default: dev)')
    args = parser.parse_args()
    
    # Load environment-specific configuration
    try:
        env_config = load_config(args.env)
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        exit(1)
    
    print(f"🚀 Creating VPC in {args.env.upper()} environment")
    print("Configuration:")
    print(f"  Region: {env_config.REGION}")
    print(f"  CIDR Block: {env_config.VPC_CIDR}")
    print(f"  AWS Profile: {env_config.PROFILE_NAME}")
    print("-" * 40)
    
    # Create VPC
    try:
        vpc_id = create_vpc(env_config, args.env)
        print(f"\n🏁 VPC creation complete! ID: {vpc_id}")
    except Exception:
        print("\n❌ VPC creation failed. See errors above.")

if __name__ == "__main__":
    main()