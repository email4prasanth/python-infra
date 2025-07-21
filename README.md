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
python infra_vpc_main.py --env dev
python destroy_vpc_main.py --env dev

# Create VPC in prod environment
python infra_vpc_main.py --env prod
python destroy_vpc_main.py --env prod
```
### How to Use create and destroy vpc and network
```sh
python infra_network_main.py --env dev
python destroy_network_main.py --env dev
```