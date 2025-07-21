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
config/__init__.py
config/dev.py
config/prod.py
vpc.py
main.py
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