from aws_cdk import aws_ec2 as ec2
from types import SimpleNamespace

class SecurityGroups:
    def __init__(self, scope, vpc, environment, config):
        self.scope = scope
        self.vpc = vpc
        self.environment = environment
        self.config = config
        self.prefix = f"testpy-{environment}"
        
        self.web_sg = self.create_web_security_group()
    
    def create_web_security_group(self) -> ec2.CfnSecurityGroup:
        """Create security group using L1 construct"""
        # Create security group
        sg = ec2.CfnSecurityGroup(
            self.scope,
            f"{self.prefix}-WebSG",
            group_description=f"{self.prefix} Web Security Group",
            vpc_id=self.vpc.ref,  # Use .ref for L1 construct
            security_group_egress=[{
                "ipProtocol": "-1",
                "cidrIp": "0.0.0.0/0",
                "description": "Allow all outbound traffic"
            }],
            tags=[{"key": "Name", "value": f"{self.prefix}-WebSG"}]
        )
        
        # Add ingress rules
        ingress_rules = []
        
        if self.environment == "dev":
            # Allow all traffic in dev
            ingress_rules.append({
                "ipProtocol": "-1",
                "cidrIp": "0.0.0.0/0",
                "description": "Allow all traffic in dev"
            })
        else:
            # Production rules: 22, 80, 443
            ingress_rules.extend([
                {
                    "ipProtocol": "tcp",
                    "fromPort": 80,
                    "toPort": 80,
                    "cidrIp": "0.0.0.0/0",
                    "description": "Allow HTTP"
                },
                {
                    "ipProtocol": "tcp",
                    "fromPort": 443,
                    "toPort": 443,
                    "cidrIp": "0.0.0.0/0",
                    "description": "Allow HTTPS"
                },
                {
                    "ipProtocol": "tcp",
                    "fromPort": 22,
                    "toPort": 22,
                    "cidrIp": "0.0.0.0/0",
                    "description": "Allow SSH"
                }
            ])
        
        # Set ingress rules
        sg.security_group_ingress = ingress_rules
        
        return sg