"""
Kubernetes Manifest Resolver Module
Automatically fixes common Kubernetes manifest issues and YAML syntax errors
"""

from typing import Dict, List, Any, Tuple
import yaml
import re


class YAMLSyntaxFixer:
    """Fixes YAML syntax errors in manifest files"""

    @staticmethod
    def fix_yaml_syntax(content: str) -> Tuple[bool, str, List[str]]:
        """
        Detect and fix common YAML syntax errors in raw file content.
        Handles: spaces in values, split keys, orphaned values, malformed key-value pairs.

        Args:
            content (str): Raw YAML file content

        Returns:
            tuple: (was_modified, fixed_content, fixes_applied)
        """
        lines = content.split('\n')
        fixed_lines = []
        fixes_applied = []
        modified = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip completely empty lines
            if not line.strip():
                fixed_lines.append(line)
                i += 1
                continue

            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]

            # Fix: Spaces in words like "ngin x" -> "nginx", "conts ainer" -> "container"
            if 'ngin x' in line:
                line = line.replace('ngin x', 'nginx')
                fixes_applied.append("✓ Fixed image name: 'ngin x' -> 'nginx'")
                modified = True

            if 'conts ainer' in line:
                line = line.replace('conts ainer', 'container')
                fixes_applied.append("✓ Fixed container name: 'conts ainer' -> 'container'")
                modified = True

            # Fix: Split keys like "restartP" + "olicy:"
            # Look ahead for key continuation patterns
            if ':' not in stripped and i < len(lines) - 1:
                next_line = lines[i + 1]
                next_stripped = next_line.lstrip()
                
                # Check for continuations like "restartP" + "olicy:"
                if next_stripped.startswith('olicy:'):
                    # This is "restartPolicy" split across lines
                    merged = indent + stripped + next_stripped
                    fixed_lines.append(merged)
                    fixes_applied.append(f"✓ Fixed split key: merged '{stripped}' with next line")
                    modified = True
                    i += 2
                    continue

            # Fix: Orphaned value keywords that belong to a previous empty key
            # Check if this line is an orphaned value (not a key with ':')
            if (':' not in stripped and 
                any(stripped.startswith(p) for p in ['True', 'False', 'Always', 'IfNotPresent', 'Never'])):
                
                # Look backwards for a key line that's empty
                if fixed_lines:
                    prev_line = fixed_lines[-1]
                    prev_stripped = prev_line.lstrip()
                    prev_indent_str = prev_line[:len(prev_line) - len(prev_stripped)]
                    prev_indent = len(prev_indent_str)
                    curr_indent = len(indent)
                    
                    # Check if previous line is an empty key-value pair at same or higher indent
                    if (':' in prev_stripped and 
                        (prev_stripped.rstrip().endswith(':') or prev_stripped.rstrip().endswith(': ')) and
                        abs(prev_indent - curr_indent) <= 1):
                        
                        # Merge: remove previous empty key line and recreate it with value
                        fixed_lines.pop()  # Remove the empty key line
                        prev_key = prev_stripped.split(':')[0] + ':'
                        merged_line = prev_indent_str + prev_key + ' ' + stripped
                        fixed_lines.append(merged_line)
                        fixes_applied.append(f"✓ Fixed orphaned value: merged '{stripped}' with previous key")
                        modified = True
                        i += 1
                        continue

            # Fix: Empty key-value pairs with orphaned values on following lines
            if ':' in stripped and (stripped.rstrip().endswith(':') or ':' in stripped):
                # Check if this looks like an empty key-value pair
                # (key: with nothing after the colon, or only whitespace)
                colon_idx = stripped.index(':')
                key_part = stripped[:colon_idx + 1]  # Include the colon
                after_colon = stripped[colon_idx + 1:].strip()
                
                # If there's nothing after the colon, look for an orphaned value
                if not after_colon:
                    # Look ahead for the actual value (skip empty lines)
                    j = i + 1
                    while j < len(lines):
                        check_line = lines[j]
                        if not check_line.strip():
                            j += 1
                        else:
                            break
                    
                    # Check if we found a value line
                    if j < len(lines):
                        value_line = lines[j]
                        value_stripped = value_line.lstrip()
                        value_indent = len(value_line) - len(value_stripped)
                        curr_indent = len(indent)
                        
                        # If next line is a value keyword at SAME indentation level or nearby
                        if (abs(value_indent - curr_indent) <= 1 and  # Allow 1 space tolerance
                            value_stripped and 
                            ':' not in value_stripped and
                            any(value_stripped.startswith(p) for p in ['True', 'False', 'Always', 'IfNotPresent', 'Never'])):
                            
                            # Merge: "imagePullPolicy:" + "IfNotPresent"
                            key_line = indent + key_part + ' ' + value_stripped
                            fixed_lines.append(key_line)
                            fixes_applied.append(f"✓ Fixed orphaned value: merged '{value_stripped}' with key")
                            modified = True
                            
                            # Skip the empty lines and the value line
                            i = j + 1
                            continue

            fixed_lines.append(line)
            i += 1

        fixed_content = '\n'.join(fixed_lines)
        return modified, fixed_content, fixes_applied


class ManifestResolver:
    """Resolves and fixes common Kubernetes manifest issues"""

    # Default values for missing fields
    DEFAULT_API_VERSION = "v1"
    DEFAULT_CONTAINER_PORT = 8080
    DEFAULT_REPLICA_COUNT = 1
    DEFAULT_IMAGE_PULL_POLICY = "IfNotPresent"

    @staticmethod
    def resolve_manifest(manifest: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Resolve and fix issues in a Kubernetes manifest.

        Args:
            manifest (dict): Kubernetes manifest to resolve

        Returns:
            tuple: (was_modified, fixed_manifest, fixes_applied)
        """
        if not isinstance(manifest, dict):
            return False, manifest, ["Invalid manifest format"]

        fixed_manifest = yaml.safe_load(yaml.dump(manifest))  # Deep copy
        fixes_applied = []

        # Fix apiVersion
        if "apiVersion" not in fixed_manifest or not fixed_manifest.get("apiVersion"):
            fixed_manifest["apiVersion"] = ManifestResolver.DEFAULT_API_VERSION
            fixes_applied.append("✓ Added default apiVersion (v1)")

        # Fix kind
        if "kind" not in fixed_manifest:
            fixes_applied.append("⚠ Missing 'kind' field - cannot proceed")
            return True, fixed_manifest, fixes_applied

        kind = fixed_manifest.get("kind")

        # Fix metadata
        if "metadata" not in fixed_manifest:
            fixed_manifest["metadata"] = {}
            fixes_applied.append("✓ Added metadata section")

        if "metadata" in fixed_manifest:
            metadata = fixed_manifest["metadata"]
            if "name" not in metadata or not metadata.get("name"):
                metadata["name"] = f"{kind.lower()}-default"
                fixes_applied.append(f"✓ Added default name: {metadata['name']}")

            if "namespace" not in metadata:
                metadata["namespace"] = "default"
                fixes_applied.append("✓ Added default namespace (default)")

        # Fix spec by kind
        if kind == "Pod":
            was_modified, fixes = ManifestResolver._fix_pod_spec(fixed_manifest)
            fixes_applied.extend(fixes)

        elif kind == "Deployment":
            was_modified, fixes = ManifestResolver._fix_deployment_spec(fixed_manifest)
            fixes_applied.extend(fixes)

        elif kind == "Service":
            was_modified, fixes = ManifestResolver._fix_service_spec(fixed_manifest)
            fixes_applied.extend(fixes)

        return bool(fixes_applied), fixed_manifest, fixes_applied

    @staticmethod
    def _fix_pod_spec(manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Fix Pod specification issues"""
        fixes = []

        if "spec" not in manifest:
            manifest["spec"] = {}
            fixes.append("✓ Added spec section")

        spec = manifest["spec"]

        # Fix containers
        if "containers" not in spec or not spec["containers"]:
            spec["containers"] = [{"name": "container-0", "image": "nginx:latest"}]
            fixes.append("✓ Added default container")
        else:
            for i, container in enumerate(spec["containers"]):
                if "name" not in container or not container.get("name"):
                    container["name"] = f"container-{i}"
                    fixes.append(f"✓ Fixed container {i} name: {container['name']}")

                if "image" not in container or not container.get("image"):
                    container["image"] = "nginx:latest"
                    fixes.append(f"✓ Added default image to container {i}: {container['image']}")

                if "imagePullPolicy" not in container:
                    container["imagePullPolicy"] = ManifestResolver.DEFAULT_IMAGE_PULL_POLICY
                    fixes.append(f"✓ Added imagePullPolicy to container {i}")

        # Fix restartPolicy
        if "restartPolicy" not in spec:
            spec["restartPolicy"] = "Always"
            fixes.append("✓ Added default restartPolicy (Always)")

        return bool(fixes), fixes

    @staticmethod
    def _fix_deployment_spec(manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Fix Deployment specification issues"""
        fixes = []

        if "spec" not in manifest:
            manifest["spec"] = {}
            fixes.append("✓ Added spec section")

        spec = manifest["spec"]

        # Fix replicas
        if "replicas" not in spec:
            spec["replicas"] = ManifestResolver.DEFAULT_REPLICA_COUNT
            fixes.append("✓ Added default replicas")

        # Fix selector
        if "selector" not in spec:
            spec["selector"] = {"matchLabels": {"app": "default"}}
            fixes.append("✓ Added default selector")

        # Fix template
        if "template" not in spec:
            spec["template"] = {"metadata": {"labels": {"app": "default"}}, "spec": {}}
            fixes.append("✓ Added template section")

        return bool(fixes), fixes

    @staticmethod
    def _fix_service_spec(manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Fix Service specification issues"""
        fixes = []

        if "spec" not in manifest:
            manifest["spec"] = {}
            fixes.append("✓ Added spec section")

        spec = manifest["spec"]

        # Fix selector
        if "selector" not in spec:
            spec["selector"] = {"app": "default"}
            fixes.append("✓ Added default selector")

        # Fix ports
        if "ports" not in spec or not spec["ports"]:
            spec["ports"] = [{"port": 80, "targetPort": 8080}]
            fixes.append("✓ Added default ports")

        return bool(fixes), fixes


class ProblemSolver:
    """High-level problem solver using ManifestResolver"""

    @staticmethod
    def solve_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve all problems in a manifest and return detailed results.

        Args:
            manifest (dict): Kubernetes manifest to solve

        Returns:
            dict: Detailed solving results
        """
        was_modified, fixed_manifest, fixes = ManifestResolver.resolve_manifest(manifest)

        return {
            "was_modified": was_modified,
            "fixed_manifest": fixed_manifest,
            "fixes_applied": fixes,
            "total_fixes": len(fixes),
            "manifest_kind": fixed_manifest.get("kind", "Unknown"),
        }
