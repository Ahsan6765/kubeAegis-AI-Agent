"""
Kubernetes validation module for kubeAegis AI Agent
Validates Kubernetes manifests and configurations
"""

import yaml
from typing import Dict, List, Any


class KubernetesValidator:
    """Validator for Kubernetes manifests and configurations"""

    REQUIRED_FIELDS = {
        "Pod": ["apiVersion", "kind", "metadata", "spec"],
        "Deployment": ["apiVersion", "kind", "metadata", "spec"],
        "Service": ["apiVersion", "kind", "metadata", "spec"],
    }

    SUPPORTED_KINDS = ["Pod", "Deployment", "Service", "ConfigMap", "Secret"]

    @staticmethod
    def validate_manifest(manifest: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a Kubernetes manifest structure.

        Args:
            manifest (dict): Kubernetes manifest to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        # Check if kind exists
        if "kind" not in manifest:
            errors.append("Missing required field: 'kind'")
            return False, errors

        kind = manifest.get("kind")

        # Check if kind is supported
        if kind not in KubernetesValidator.SUPPORTED_KINDS:
            errors.append(f"Unsupported Kubernetes kind: {kind}")

        # Validate required fields for specific kinds
        if kind in KubernetesValidator.REQUIRED_FIELDS:
            required = KubernetesValidator.REQUIRED_FIELDS[kind]
            for field in required:
                if field not in manifest:
                    errors.append(f"Missing required field for {kind}: '{field}'")

        # Validate apiVersion
        if "apiVersion" in manifest:
            api_version = manifest["apiVersion"]
            if not isinstance(api_version, str) or not api_version.strip():
                errors.append("Invalid apiVersion: must be a non-empty string")

        # Validate metadata
        if "metadata" in manifest:
            metadata = manifest["metadata"]
            if not isinstance(metadata, dict):
                errors.append("Invalid metadata: must be a dictionary")
            elif "name" not in metadata:
                errors.append("Missing required field in metadata: 'name'")

        return len(errors) == 0, errors

    @staticmethod
    def validate_pod_spec(pod_spec: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate Pod specification.

        Args:
            pod_spec (dict): Pod spec to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        if "containers" not in pod_spec:
            errors.append("Missing required field in spec: 'containers'")
            return False, errors

        containers = pod_spec.get("containers")
        if not isinstance(containers, list) or len(containers) == 0:
            errors.append("Containers must be a non-empty list")
            return False, errors

        for idx, container in enumerate(containers):
            if "name" not in container:
                errors.append(f"Container {idx}: missing required field 'name'")
            if "image" not in container:
                errors.append(f"Container {idx}: missing required field 'image'")

        return len(errors) == 0, errors


class ManifestValidator:
    """Validate Kubernetes manifests from files"""

    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, List[str]]:
        """
        Validate a Kubernetes manifest file.

        Args:
            file_path (str): Path to manifest file

        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if data is None:
                return False, ["File is empty or contains only whitespace"]

            if not isinstance(data, dict):
                return False, ["Manifest must be a valid YAML dictionary"]

            return KubernetesValidator.validate_manifest(data)

        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]
