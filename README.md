# python-infra
- The main aim to create aws infra strcture that can launch ec2 and rds.
- check the version `python --version`, if require install and add in the envrionment varibales.
- Install boto3
```sh
pip install boto3
pip show boto3
```
- Check the available profiles and chose the profile where the resources need to deploy. Run
```
python check_credentials.py
```
- Create the following py files
```sh
# Configuration files
config/__init__.py
config/dev.py
config/prod.py
# Destruction modules
destroy/__init__.py
destroy/destruct_ec2server1.py
destroy/destruct_ec2server2.py
destroy/destruct_network.py
destroy/destruct_vpc.py
# Infrastructure creation modules
infra/__init__.py
infra/infra_ec2server1.py
infra/infra_ec2server2.py
infra/infra_network.py
infra/infra_vpc.py
# Executable scripts
scripts/deploy_ec2server1.py
scripts/deploy_ec2server2.py
scripts/deploy_network.py
scripts/deploy_vpc.py
scripts/destory_ec2server1.py
scripts/destory_ec2server2.py
scripts/destroy_network.py
scripts/destroy_vpc.py
# Shared utilities
utils/ __init__.py
utils/ path_utils.py      # Utility for path resolution
utils/ aws_utils.py
```
### How to create and destroy ec2 server-1
```sh
# Create ec2 ubuntu server in dev environment
python scripts/deploy_network.py -e dev
python scripts/deploy_ec2server1.py -e dev
python scripts/destroy_ec2server1.py -e dev
python scripts/destroy_network.py -e dev
```
### How to Create ec2 in prod environment
```sh
# Create ec2 linux server in prod environment
python scripts/deploy_network.py -e prod
python scripts/deploy_ec2server2.py -e prod
python scripts/destroy_ec2server2.py -e prod
 python scripts/destroy_network.py -e prod
```