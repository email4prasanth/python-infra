import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ProfileNotFound

def check_aws_credentials(profile_name):
    try:
        # Create session with specified profile or default
        session = boto3.Session(profile_name=profile_name)
        sts = session.client('sts')
        
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Credentials Valid for profile: '{profile_name or 'default'}'!")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        return True
        
    except ProfileNotFound:
        print(f"❌ Profile '{profile_name}' not found in AWS configuration")
        print("Check your ~/.aws/config and ~/.aws/credentials files")
        return False
    except NoCredentialsError:
        print(f"❌ No AWS credentials found for profile '{profile_name}'")
        print("Configure with: aws configure --profile " + (profile_name or "default"))
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ Credentials error ({error_code}) for profile '{profile_name}': {error_msg}")
        return False

if __name__ == "__main__":
    # Specify the profile name you want to check
    profile_to_check = "tut"
    check_aws_credentials("tut")