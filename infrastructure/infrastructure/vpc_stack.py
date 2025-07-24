from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct
import importlib
from types import SimpleNamespace

class VPCStack(Stack):
    def load_config(self, env: str):
        try:
            module = importlib.import_module(f"infrastructure.config.{env}")
            return SimpleNamespace(**vars(module))
        except ModuleNotFoundError:
            raise ValueError(f"Configuration for {env} not found")

    def __init__(self, scope: Construct, construct_id: str, environment: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = self.load_config(environment)
        prefix = f"testpy-{environment}"

        # Create VPC
        self.vpc = ec2.CfnVPC(
            self,
            "Vpc",
            cidr_block=config.VPC_CIDR,
            tags=[{"key": "Name", "value": f"{prefix}-vpc"}]
        )
        
        # Create Internet Gateway
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnInternetGateway.html
        self.igw = ec2.CfnInternetGateway(
            self,
            "IGW",
            tags=[{"key": "Name", "value": f"{prefix}-IGW"}]
        )
        
        # Attach IGW to VPC
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnVPCGatewayAttachment.html
        ec2.CfnVPCGatewayAttachment(
            self,
            "IGWAttach",
            vpc_id=self.vpc.ref,
            internet_gateway_id=self.igw.ref
        )
        
        # Create Route Table
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnRouteTable.html
        self.route_table = ec2.CfnRouteTable(
            self,
            "RouteTable",
            vpc_id=self.vpc.ref,
            tags=[{"key": "Name", "value": f"{prefix}-RT"}]
        )
        
        # Add default route to internet
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnRoute.html
        ec2.CfnRoute(
            self,
            "DefaultRoute",
            route_table_id=self.route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.igw.ref
        )
        
        # Create Public Subnet
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSubnet.html
        self.public_subnet = ec2.CfnSubnet(
            self,
            "PublicSubnet",
            vpc_id=self.vpc.ref,
            cidr_block=config.PUBLIC_SUBNET_CIDR,
            availability_zone=config.AVAILABILITY_ZONE,
            tags=[{"key": "Name", "value": f"{prefix}-PublicSubnet1"}]
        )
        
        # Associate subnet with route table
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSubnetRouteTableAssociation.html
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "SubnetRouteAssoc",
            subnet_id=self.public_subnet.ref,
            route_table_id=self.route_table.ref
        )

        # Output VPC ID
        CfnOutput(self, "VpcId", value=self.vpc.ref)
        CfnOutput(self, "PublicSubnetId", value=self.public_subnet.ref)
        CfnOutput(self, "RouteTableId", value=self.route_table.ref)