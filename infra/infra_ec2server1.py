import boto3
from botocore.exceptions import ClientError

def create_ec2_server1(env_config, environment, subnet_id, security_group_id):
    try:
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        instance_name = f"py-infra-{environment}-server1"
        
        # Create instance
        instances = ec2.run_instances(
            ImageId=env_config.SERVER1_AMI,
            InstanceType=env_config.INSTANCE_TYPE,
            KeyName=env_config.KEY_NAME,
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[
                {
                    'DeviceIndex': 0,
                    'SubnetId': subnet_id,
                    'Groups': [security_group_id],
                    'AssociatePublicIpAddress': True
                }
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': instance_name},
                        {'Key': 'Environment', 'Value': environment},
                        {'Key': 'Project', 'Value': 'py-infra'}
                    ]
                }
            ]
        )
        
        instance_id = instances['Instances'][0]['InstanceId']
        print(f"✅ EC2 Server1 (Ubuntu) created: {instance_name} ({instance_id})")
        return instance_id
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        raise