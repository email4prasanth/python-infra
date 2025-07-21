# config/__init__.py
import importlib

def load_config(env):
    """Dynamically load configuration for the specified environment"""
    try:
        module = importlib.import_module(f"config.{env}")
        return module
    except ImportError:
        raise ValueError(f"Invalid environment: {env}. Valid options: dev, prod")