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
### How to Use create and destroy vpc
```sh
# Create VPC in dev environment
cd scripts
python deploy_vpc.py --env dev
python destroy_vpc.py --env dev

# Create VPC in prod environment
python deploy_vpc.py --env prod
python destroy_vpc.py --env prod
```
### How to Use create and destroy vpc and network
```sh
python deploy_network.py --env dev
python destroy_network.py --env dev

python deploy_network.py --env prod
python destroy_network.py --env prod
```