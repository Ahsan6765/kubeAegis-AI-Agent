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
from tools.k8s_resolver import ManifestResolver, YAMLSyntaxFixer
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

    def resolve_manifest_file(self, file_path: str, output_file: str = None) -> dict:
        """
        Resolve and fix issues in a manifest file.

        Args:
            file_path (str): Path to manifest file
            output_file (str): Optional output file path (if None, prints YAML)

        Returns:
            dict: Resolution result with fixes applied
        """
        try:
            manifest = load_yaml(file_path)
            return self.resolve_manifest_content(manifest, output_file)
        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "message": str(e),
            }

    def resolve_manifest_content(self, manifest: dict, output_file: str = None) -> dict:
        """
        Resolve and fix issues in manifest content.

        Args:
            manifest (dict): Kubernetes manifest dictionary
            output_file (str): Optional output file path

        Returns:
            dict: Resolution result with fixes applied
        """
        import yaml

        try:
            was_modified, fixed_manifest, fixes = ManifestResolver.resolve_manifest(manifest)

            # Validate the fixed manifest
            is_valid, errors = self.validator.validate_manifest(fixed_manifest)

            result = {
                "status": "resolved" if was_modified else "valid",
                "was_modified": was_modified,
                "fixed_manifest": fixed_manifest,
                "fixes_applied": fixes,
                "total_fixes": len(fixes),
                "manifest_kind": fixed_manifest.get("kind", "Unknown"),
                "validation_status": "valid" if is_valid else "invalid",
                "validation_errors": errors,
            }

            # Write to output file if specified
            if output_file and was_modified:
                with open(output_file, "w") as f:
                    yaml.dump(fixed_manifest, f, default_flow_style=False)
                result["output_file"] = output_file

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def auto_resolve_and_validate(self, file_path: str) -> dict:
        """
        Automatically resolve issues and validate the fixed manifest.

        Args:
            file_path (str): Path to manifest file

        Returns:
            dict: Combined validation and resolution results
        """
        try:
            manifest = load_yaml(file_path)

            # First, resolve issues
            resolution_result = self.resolve_manifest_content(manifest)

            # Then validate the fixed manifest
            fixed_manifest = resolution_result["fixed_manifest"]
            is_valid, errors = self.validator.validate_manifest(fixed_manifest)

            return {
                "original_file": file_path,
                "resolution": resolution_result,
                "validation": {
                    "status": "valid" if is_valid else "invalid",
                    "errors": errors,
                },
                "overall_status": "success" if is_valid else "partial_success",
            }

        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "message": str(e),
            }

    def fix_manifest_in_place(self, file_path: str) -> dict:
        """
        Detect and fix errors in a manifest file, overwriting the original file.
        Handles both YAML syntax errors and Kubernetes semantic errors.

        Args:
            file_path (str): Path to manifest file to fix in-place

        Returns:
            dict: Fix result with before/after details
        """
        try:
            import yaml

            # Step 0: Read raw file content
            with open(file_path, "r") as f:
                raw_content = f.read()

            # Step 1: Try to parse and validate original
            try:
                manifest = load_yaml(file_path)
                original_valid, original_errors = self.validator.validate_manifest(manifest)
                syntax_errors = []
            except Exception as syntax_error:
                # YAML has syntax errors - need to fix them first
                original_valid = False
                syntax_errors = [str(syntax_error)]
                original_errors = [str(syntax_error)]
                manifest = None

            # Step 1.5: If YAML syntax error, try to fix it
            all_fixes = []
            if syntax_errors:
                yaml_fixed, fixed_content, yaml_fixes = YAMLSyntaxFixer.fix_yaml_syntax(raw_content)
                all_fixes.extend(yaml_fixes)

                if yaml_fixed:
                    # Try to parse the fixed YAML
                    try:
                        manifest = yaml.safe_load(fixed_content)
                        raw_content = fixed_content  # Update content for later writing
                        original_valid, original_errors = self.validator.validate_manifest(manifest)
                        syntax_errors = []  # Syntax is now fixed
                    except Exception as still_broken:
                        # Still has syntax errors after fixing attempt
                        return {
                            "status": "error",
                            "file": file_path,
                            "message": f"YAML syntax error after fix attempt: {still_broken}",
                            "was_modified": False,
                            "fixes_applied": all_fixes,
                        }
                else:
                    # Fixing didn't help
                    return {
                        "status": "error",
                        "file": file_path,
                        "message": f"Could not fix YAML syntax error: {syntax_errors[0]}",
                        "was_modified": False,
                        "fixes_applied": all_fixes,
                    }

            # Step 2: If already valid, return success
            if original_valid:
                if all_fixes:
                    # We fixed syntax errors but manifest is now valid
                    with open(file_path, "w") as f:
                        f.write(raw_content)
                    return {
                        "status": "fixed",
                        "file": file_path,
                        "message": f"Fixed {len(all_fixes)} syntax issue(s)",
                        "was_modified": True,
                        "fixes_applied": all_fixes,
                        "total_fixes": len(all_fixes),
                        "fixed_manifest": manifest,
                        "original_errors": [],
                        "final_validation": {
                            "status": "valid",
                            "errors": [],
                        },
                    }
                else:
                    return {
                        "status": "already_valid",
                        "file": file_path,
                        "message": "Manifest is already valid, no fixes needed",
                        "was_modified": False,
                        "fixes_applied": [],
                        "total_fixes": 0,
                    }

            # Step 3: Resolve/fix semantic issues in the manifest
            was_modified, fixed_manifest, semantic_fixes = ManifestResolver.resolve_manifest(
                manifest
            )
            all_fixes.extend(semantic_fixes)

            # Step 4: Validate the fixed manifest
            is_valid, errors = self.validator.validate_manifest(fixed_manifest)

            # Step 5: Overwrite the original file with fixed version
            if was_modified or syntax_errors:
                with open(file_path, "w") as f:
                    yaml.dump(fixed_manifest, f, default_flow_style=False)

            return {
                "status": "fixed" if (was_modified or syntax_errors) else "no_changes",
                "file": file_path,
                "was_modified": was_modified or bool(syntax_errors),
                "original_errors": original_errors,
                "fixes_applied": all_fixes,
                "total_fixes": len(all_fixes),
                "fixed_manifest": fixed_manifest,
                "final_validation": {
                    "status": "valid" if is_valid else "invalid",
                    "errors": errors,
                },
                "message": f"Fixed {len(all_fixes)} issues in {file_path}" if all_fixes else f"No issues found in {file_path}",
            }

        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "message": str(e),
                "was_modified": False,
            }

