"""
Brain module for kubeAegis AI Agent
Core intelligence and orchestration logic
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.yaml_loader import load_yaml
from tools.k8s_validator import ManifestValidator, KubernetesValidator
from config import Config


class KubeAegisAgent:
    """Main AI Agent for Kubernetes management and validation"""

    def __init__(self, config=None):
        """
        Initialize the KubeAegis Agent.

        Args:
            config (Config): Configuration object (uses default if None)
        """
        self.config = config or Config
        self.validator = KubernetesValidator()

    def validate_manifest_file(self, file_path: str) -> dict:
        """
        Validate a Kubernetes manifest file.

        Args:
            file_path (str): Path to manifest file

        Returns:
            dict: Validation result with status and messages
        """
        is_valid, errors = ManifestValidator.validate_file(file_path)

        return {
            "status": "valid" if is_valid else "invalid",
            "file": file_path,
            "errors": errors,
        }

    def validate_manifest_content(self, manifest: dict) -> dict:
        """
        Validate Kubernetes manifest content.

        Args:
            manifest (dict): Kubernetes manifest dictionary

        Returns:
            dict: Validation result with status and messages
        """
        is_valid, errors = self.validator.validate_manifest(manifest)

        return {
            "status": "valid" if is_valid else "invalid",
            "manifest_kind": manifest.get("kind", "Unknown"),
            "errors": errors,
        }

    def get_configuration(self) -> dict:
        """Get agent configuration"""
        return self.config.get_config()

    def health_check(self) -> dict:
        """
        Perform agent health check.

        Returns:
            dict: Health status information
        """
        return {
            "status": "healthy",
            "version": "0.1.0",
            "config": self.get_configuration(),
        }
