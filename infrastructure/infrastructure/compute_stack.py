from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct
import importlib
from types import SimpleNamespace

class ComputeStack(Stack):
    def load_config(self, env: str):
        try:
            module = importlib.import_module(f"infrastructure.config.{env}")
            return SimpleNamespace(**vars(module))
        except ModuleNotFoundError:
            raise ValueError(f"Configuration for {env} not found")
    
    def __init__(self, 
                 scope: Construct, 
                 construct_id: str, 
                 environment: str, 
                 security_group_id: str,
                 public_subnets: list,
                 **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = self.load_config(environment)
        prefix = f"testpy-{environment}"

        # Create EC2 Ubuntu instances
        self.server1 = ec2.CfnInstance(
            self,
            f"{prefix}-Ubuntu",
            instance_type=config.INSTANCE_TYPE,
            key_name=config.KEY_NAME,
            image_id=config.SERVER1_AMI,
            # subnet_id=public_subnets[0].ref,
            # security_group_ids=security_group_id, 
            # availability_zone=config.AVAILABILITY_ZONES[0],
            tags=[{"key": "Name", "value": f"{prefix}-Ubuntu"}],
            # Enable public IP and networking
            network_interfaces=[ec2.CfnInstance.NetworkInterfaceProperty(
                device_index="0",
                associate_public_ip_address=True,
                delete_on_termination=True,
                description="Ubuntu server",
                subnet_id=public_subnets[0].ref,
                group_set=[security_group_id]  
            )
            ]
        )
        # Create EC2 Linux instances 
        self.server2 = ec2.CfnInstance(
            self,
            f"{prefix}-Linux",
            instance_type=config.INSTANCE_TYPE,
            key_name=config.KEY_NAME,
            image_id=config.SERVER2_AMI,
            # subnet_id=public_subnets[0].ref,
            # security_group_ids=security_group_id,
            # availability_zone=config.AVAILABILITY_ZONES[1],
            tags=[{"key": "Name", "value": f"{prefix}-Linux"}],
            # Enable public IP and networking
            network_interfaces=[ec2.CfnInstance.NetworkInterfaceProperty(
                device_index="0",
                associate_public_ip_address=True,
                delete_on_termination=True,
                description="Linux server",
                subnet_id=public_subnets[1].ref,
                group_set=[security_group_id]  
            )
            ]
        )

        # Output instance IDs
        CfnOutput(self, "Server1Id", value=self.server1.ref)
        CfnOutput(self, "Server2Id", value=self.server2.ref)
        CfnOutput(self, "Server1PublicIp", value=self.server1.attr_public_ip)
        CfnOutput(self, "Server2PublicIp", value=self.server2.attr_public_ip)
