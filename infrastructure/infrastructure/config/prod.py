# Production environment configuration
REGION = "us-east-1"
VPC_CIDR = "10.1.0.0/16"
PUBLIC_SUBNET_CIDRS = ["10.1.1.0/24", "10.1.2.0/24"]
AVAILABILITY_ZONES = ["us-east-1a", "us-east-1b"]
PROFILE_NAME = "tut"
INSTANCE_TYPE = "t2.micro"
KEY_NAME = "DevOpsKey"
SERVER1_AMI = "ami-020cba7c55df1f615"  # Ubuntu Server 24.04 LTS
SERVER2_AMI = "ami-050fd9796aa387c0d"  # Amazon Linux 2023