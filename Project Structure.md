python-infra/
├── config/                # Configuration files
│   ├── __init__.py
│   ├── dev.py
│   └── prod.py
├── infra/                 # Infrastructure creation modules
│   ├── __init__.py
│   ├── infra_network.py
│   └── infra_vpc.py
├── destroy/               # Destruction modules
│   ├── __init__.py
│   ├── destruct_network.py
│   └── destruct_vpc.py
├── scripts/               # Executable scripts
│   ├── deploy_network.py
│   ├── deploy_vpc.py
│   ├── destroy_network.py
│   └── destroy_vpc.py
└── utils/                 # Shared utilities
    ├── __init__.py
    └── path_utils.py      # Utility for path resolution