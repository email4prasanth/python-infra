### python-infra Intial setup
- The main aim to create aws infra strcture s3.
- check the version `python --version`, if require install and add in the envrionment varibales.
- Install boto3
```sh
# Install AWS CLI and configure
aws --version
# nstall AWS CDK using node
node --version
npm --version
npm install -g aws-cdk
cdk --version
# Install python
python --version
# Create folder structure
mkdir infrastructure
New-Item infrastructure\config\__init__.py -ItemType File
New-Item infrastructure\config\dev.py -ItemType File
New-Item infrastructure\config\prod.py -ItemType File
```
### python infra creation
```sh
cd .\infrastructure\
.\.venv\Scripts\Activate.ps1
cdk bootstrap aws://180294218712/us-east-1 --profile tut
cdk bootstrap aws://180294218712/us-east-1 --profile tut
    # # The above will infulence following services
    # AWS::CloudFormation::Stack (1)
    # AWS::ECR::Repository (1)
    # AWS::IAM::Role (6)
    # AWS::IAM::Policy ()
    # AWS::SSM::Parameter (1)
pip install -r requirements.txt
python -m pip show aws-cdk-lib
python -m pip show constructs
cdk synth -c env=dev --profile tut --region us-east-1
cdk deploy --profile tut -c env=dev
cdk destroy --profile tut -c env=dev --force
aws cloudformation delete-stack --stack-name CDKToolkit --profile tut
deactivate
cd ..
aws s3 ls --profile tut --region us-east-1
.\z-delete-cdk-buckets.ps1
aws s3 ls --profile tut --region us-east-1
```

--------lambda and api------------
https://www.youtube.com/watch?v=o3s4VqlMsT8
https://docs.aws.amazon.com/cdk/api/v2/python/