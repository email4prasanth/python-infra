```sh
python-infra/
├── config/                # Configuration files
│   ├── __init__.py
│   ├── dev.py
│   └── prod.py
├── destroy/               # Destruction modules
│   ├── __init__.py
│   ├── destruct_ec2server1.py
│   ├── destruct_ec2server2.py
│   ├── destruct_network.py
│   └── destruct_vpc.py
├── infra/                 # Infrastructure creation modules
│   ├── __init__.py
│   ├── infra_ec2server1.py
│   ├── infra_ec2server2.py
│   ├── infra_network.py
│   └── infra_vpc.py
├── scripts/               # Executable scripts
│   ├── deploy_ec2server1.py
│   ├── deploy_ec2server2.py
│   ├── deploy_network.py
│   ├── deploy_vpc.py
│   ├── destory_ec2server1.py
│   ├── destory_ec2server2.py
│   ├── destroy_network.py
│   └── destroy_vpc.py
└── utils/                 # Shared utilities
    ├── __init__.py
    └── path_utils.py      # Utility for path resolution
    └── aws_utils.py
```