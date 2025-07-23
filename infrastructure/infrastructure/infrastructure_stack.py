from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags, 
    CfnOutput
)
from constructs import Construct
import importlib
from types import SimpleNamespace

class InfrastructureStack(Stack):
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
        vpc = ec2.CfnVPC(
            self,
            "Vpc",
            cidr_block=config.VPC_CIDR,
            tags=[{"key": "Name", "value": f"{prefix}-vpc"}]
        )
        
        # Create Internet Gateway
        igw = ec2.CfnInternetGateway(
            self,
            "IGW",
            tags=[{"key": "Name", "value": f"{prefix}-IGW"}]
        )
        
        # Attach IGW to VPC
        ec2.CfnVPCGatewayAttachment(
            self,
            "IGWAttach",
            vpc_id=vpc.ref,
            internet_gateway_id=igw.ref
        )
        
        # Create Route Table
        route_table = ec2.CfnRouteTable(
            self,
            "RouteTable",
            vpc_id=vpc.ref,
            tags=[{"key": "Name", "value": f"{prefix}-RT"}]
        )
        
        # Add default route to internet
        ec2.CfnRoute(
            self,
            "DefaultRoute",
            route_table_id=route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.ref
        )
        
        # Create Public Subnet
        subnet = ec2.CfnSubnet(
            self,
            "PublicSubnet",
            vpc_id=vpc.ref,
            cidr_block=config.PUBLIC_SUBNET_CIDR,
            availability_zone=config.AVAILABILITY_ZONE,
            tags=[{"key": "Name", "value": f"{prefix}-PublicSubnet1"}]
        )
        
        # Associate subnet with route table
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "SubnetRouteAssoc",
            subnet_id=subnet.ref,
            route_table_id=route_table.ref
        )
        
        # Output VPC ID
        CfnOutput(self, "VpcId", value=vpc.ref)
        CfnOutput(self, "PublicSubnetId", value=subnet.ref)