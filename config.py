"""
Configuration module for kubeAegis AI Agent
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Kubernetes configuration
KUBECONFIG_PATH = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))
KUBERNETES_CONTEXT = os.getenv("KUBERNETES_CONTEXT", None)
KUBERNETES_NAMESPACE = os.getenv("KUBERNETES_NAMESPACE", "default")

# YAML validation settings
YAML_VALIDATION_ENABLED = os.getenv("YAML_VALIDATION_ENABLED", "true").lower() == "true"
STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "false").lower() == "true"

# Agent configuration
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class Config:
    """Configuration class for application settings"""

    kubeconfig = KUBECONFIG_PATH
    kubernetes_namespace = KUBERNETES_NAMESPACE
    yaml_validation_enabled = YAML_VALIDATION_ENABLED
    strict_validation = STRICT_VALIDATION
    debug_mode = DEBUG_MODE
    log_level = LOG_LEVEL

    @classmethod
    def get_config(cls):
        """Get configuration as dictionary"""
        return {
            "kubeconfig": cls.kubeconfig,
            "namespace": cls.kubernetes_namespace,
            "yaml_validation": cls.yaml_validation_enabled,
            "strict_validation": cls.strict_validation,
            "debug_mode": cls.debug_mode,
            "log_level": cls.log_level,
        }
