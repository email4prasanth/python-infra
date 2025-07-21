import boto3
import time
from botocore.exceptions import ClientError

def destroy_ec2_server2(env_config, environment):
    try:
        session = boto3.Session(profile_name=env_config.PROFILE_NAME)
        ec2 = session.client('ec2', region_name=env_config.REGION)
        
        instance_name = f"py-infra-{environment}-server2"
        
        # Find instance by name
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [instance_name]},
                {'Name': 'tag:Environment', 'Values': [environment]},
                {'Name': 'tag:Project', 'Values': ['py-infra']},
                {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
            ]
        )
        
        instance_ids = []
        for res in response['Reservations']:
            for inst in res['Instances']:
                instance_ids.append(inst['InstanceId'])
                print(f"🔍 Found Server2: {instance_name} ({inst['InstanceId']})")
        
        if not instance_ids:
            print(f"✅ No Server2 instance found: {instance_name}")
            return True
            
        # Terminate instance
        ec2.terminate_instances(InstanceIds=instance_ids)
        print("🗑️ Terminating Server2 instance...")
        
        # Wait for termination
        print("⏳ Waiting for instance to terminate...", end='', flush=True)
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instance_ids)
        print("\n✅ Server2 instance terminated")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_msg}")
        return False