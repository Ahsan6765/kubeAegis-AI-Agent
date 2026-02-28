# kubeAegis AI Agent

A powerful AI-driven agent for validating, analyzing, and managing Kubernetes manifests.

## Overview

kubeAegis is a comprehensive Kubernetes validation and management tool designed to help DevOps engineers and system administrators ensure their Kubernetes configurations are correct, secure, and follow best practices.

## Features

- ✅ **Manifest Validation**: Validate Kubernetes YAML manifests against best practices
- 🔍 **Deep Analysis**: Analyze manifest structure and identify potential issues
- ⚙️ **Configurable**: Flexible configuration through environment variables
- 🎯 **CLI Tool**: Easy-to-use command-line interface
- 📦 **Modular Design**: Clean, extensible architecture

## Project Structure

```
kubeAegis-AI-Agent/
├── cli.py                 # Command-line interface
├── config.py              # Configuration module
├── requirements.txt       # Python dependencies
├── pod.yaml              # Example Kubernetes manifest
├── README.md             # This file
├── agent/
│   ├── __init__.py
│   └── brain.py          # Core AI agent logic
└── tools/
    ├── __init__.py
    ├── k8s_validator.py  # Kubernetes validation tools
    └── yaml_loader.py    # YAML file loading utilities
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or navigate to the project directory:
```bash
cd kubeAegis-AI-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Configure the agent using environment variables:

```bash
# Kubernetes configuration
export KUBECONFIG=~/.kube/config
export KUBERNETES_CONTEXT=default
export KUBERNETES_NAMESPACE=default

# Validation settings
export YAML_VALIDATION_ENABLED=true
export STRICT_VALIDATION=false

# Agent configuration
export DEBUG_MODE=false
export LOG_LEVEL=INFO
```

## Usage

### Validate a Manifest

```bash
python cli.py validate pod.yaml
```

### Analyze a Manifest

```bash
python cli.py analyze pod.yaml
```

### Check Agent Configuration

```bash
python cli.py config
```

### Check Agent Health

```bash
python cli.py health
```

### Get Help

```bash
python cli.py --help
```

## Module Overview

### config.py
Centralized configuration management with support for environment variables.

**Key Classes:**
- `Config`: Configuration class for application settings

### agent/brain.py
Core intelligence and orchestration logic for the AI agent.

**Key Classes:**
- `KubeAegisAgent`: Main agent class with validation and analysis capabilities

### tools/k8s_validator.py
Kubernetes manifest validation and verification.

**Key Classes:**
- `KubernetesValidator`: Validates manifest structure and content
- `ManifestValidator`: File-based validation

### tools/yaml_loader.py
Utilities for safely loading and parsing YAML files.

**Functions:**
- `load_yaml()`: Load and parse YAML files with error handling

## Example Usage

### Python API

```python
from agent.brain import KubeAegisAgent
from config import Config

# Initialize agent
agent = KubeAegisAgent()

# Validate a manifest file
result = agent.validate_manifest_file("pod.yaml")
print(result)

# Check agent health
health = agent.health_check()
print(health)

# Get configuration
config = agent.get_configuration()
print(config)
```

## Error Handling

The agent provides comprehensive error handling:

- **File Not Found**: Clear message when manifest file doesn't exist
- **YAML Parsing Errors**: Detailed error messages for invalid YAML
- **Validation Errors**: List of specific validation issues found
- **Configuration Errors**: Warnings about missing or invalid configuration

## Supported Kubernetes Resources

Currently supported resource kinds:
- Pod
- Deployment
- Service
- ConfigMap
- Secret

## Development

### Running Tests

```bash
# Validate the example pod.yaml
python cli.py validate pod.yaml
```

### Project Dependencies

- **PyYAML** (6.0.1): YAML parsing
- **kubernetes** (28.1.0): Kubernetes Python client
- **click** (8.1.7): CLI framework

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'yaml'`
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Issue: `File not found` error
**Solution**: Ensure the manifest file path is correct and the file exists

### Issue: YAML parsing errors
**Solution**: Verify your YAML syntax is valid (proper indentation, quoted values, etc.)

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Write clean, documented code
2. Test changes with example manifests
3. Update documentation as needed

## License

This project is part of the DevOps toolkit.

## Support

For issues, questions, or suggestions, please contact the DevOps team.

## Changelog

### Version 0.1.0 (Initial Release)
- Initial project structure
- Manifest validation
- Basic CLI interface
- Configuration management
