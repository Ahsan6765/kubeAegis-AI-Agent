"""
CLI module for kubeAegis AI Agent
Command-line interface for managing and validating Kubernetes manifests
"""

import sys
import os
from pathlib import Path

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from agent.brain import KubeAegisAgent
from config import Config


@click.group()
@click.version_option(version="0.1.0", prog_name="kubeAegis")
def cli():
    """
    kubeAegis AI Agent - Kubernetes Validation and Management

    A powerful AI-driven agent for validating and managing Kubernetes manifests.
    """
    pass


@cli.command()
@click.argument("manifest_file", type=click.Path(exists=True))
def validate(manifest_file):
    """Validate a Kubernetes manifest file."""
    agent = KubeAegisAgent()

    click.echo(f"Validating manifest: {manifest_file}")
    click.echo("-" * 60)

    result = agent.validate_manifest_file(manifest_file)

    if result["status"] == "valid":
        click.secho("✓ Manifest is valid!", fg="green", bold=True)
    else:
        click.secho("✗ Manifest is invalid:", fg="red", bold=True)
        for error in result["errors"]:
            click.secho(f"  - {error}", fg="red")

    return result


@cli.command()
def config():
    """Display agent configuration."""
    agent = KubeAegisAgent()
    cfg = agent.get_configuration()

    click.echo("kubeAegis Agent Configuration")
    click.echo("-" * 60)
    for key, value in cfg.items():
        click.echo(f"{key.replace('_', ' ').title():.<40} {value}")


@cli.command()
def health():
    """Check agent health status."""
    agent = KubeAegisAgent()
    status = agent.health_check()

    click.secho("kubeAegis Agent Health Check", bold=True)
    click.echo("-" * 60)
    click.secho(f"Status: {status['status'].upper()}", fg="green", bold=True)
    click.echo(f"Version: {status['version']}")
    click.echo("\nConfiguration:")
    for key, value in status["config"].items():
        click.echo(f"  {key.replace('_', ' ').title()}: {value}")


@cli.command()
@click.argument("manifest_file", type=click.Path(exists=True))
def analyze(manifest_file):
    """Analyze a Kubernetes manifest file."""
    from tools.yaml_loader import load_yaml

    click.echo(f"Analyzing manifest: {manifest_file}")
    click.echo("-" * 60)

    try:
        manifest = load_yaml(manifest_file)
        agent = KubeAegisAgent()

        result = agent.validate_manifest_content(manifest)

        click.echo(f"Kind: {result['manifest_kind']}")
        click.echo(f"Status: {result['status'].upper()}")

        if result["errors"]:
            click.secho("Issues found:", fg="yellow", bold=True)
            for error in result["errors"]:
                click.secho(f"  - {error}", fg="yellow")
        else:
            click.secho("No issues found!", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


@cli.command()
@click.argument("manifest_file", type=click.Path(exists=True))
def fix(manifest_file):
    """Fix errors in a Kubernetes manifest file (overwrites original)."""
    agent = KubeAegisAgent()

    if not os.path.exists(manifest_file):
        click.secho(f"Error: File '{manifest_file}' not found", fg="red")
        sys.exit(1)

    click.echo(click.style(f"🔧 Fixing manifest: {manifest_file}", fg="cyan", bold=True))
    click.echo(click.style("-" * 60, fg="cyan"))

    result = agent.fix_manifest_in_place(manifest_file)

    if result["status"] == "error":
        click.secho(f"✗ Error: {result['message']}", fg="red")
        sys.exit(1)

    if result["status"] == "already_valid":
        click.secho("✓ Manifest is already valid!", fg="green")
        click.echo(f"  File: {result['file']}")
        return

    # Show what was fixed
    click.secho(f"✓ Fixed {result['total_fixes']} issue(s)", fg="green", bold=True)

    if result["fixes_applied"]:
        click.echo("\nFixes applied:")
        for i, fix_desc in enumerate(result["fixes_applied"], 1):
            click.secho(f"  {i}. {fix_desc}", fg="green")

    # Show original errors
    if result["original_errors"]:
        click.echo(click.style("\nOriginal errors detected:", fg="red"))
        for error in result["original_errors"]:
            click.secho(f"  • {error}", fg="red")

    # Final validation status
    final_status = result["final_validation"]["status"]
    if final_status == "valid":
        click.secho("✓ Final validation: PASSED", fg="green", bold=True)
    else:
        click.secho("✗ Final validation: FAILED", fg="red", bold=True)
        if result["final_validation"]["errors"]:
            for error in result["final_validation"]["errors"]:
                click.secho(f"  • {error}", fg="red")

    click.echo(click.style("-" * 60, fg="cyan"))
    click.secho(f"✓ {result['file']} has been fixed and overwritten", fg="green", bold=True)


@cli.command()
@click.argument("manifest_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file for fixed manifest (optional)",
)
def resolve(manifest_file, output):
    """Automatically resolve and fix Kubernetes manifest issues."""
    agent = KubeAegisAgent()

    click.echo(f"🔧 Resolving manifest: {manifest_file}")
    click.echo("=" * 70)

    try:
        # Step 1: Validate original manifest
        click.echo("\n📋 Step 1: Analyzing original manifest...")
        click.echo("-" * 70)
        validation_result = agent.validate_manifest_file(manifest_file)

        if validation_result["status"] == "valid":
            click.secho("✓ Manifest is already valid!", fg="green", bold=True)
            click.echo("\nNo fixes needed!")
            return

        click.secho("✗ Issues detected:", fg="red")
        for error in validation_result["errors"]:
            click.secho(f"  - {error}", fg="red")

        # Step 2: Resolve issues
        click.echo("\n🔨 Step 2: Resolving detected issues...")
        click.echo("-" * 70)

        resolution_result = agent.resolve_manifest_file(manifest_file, output)

        if resolution_result["status"] == "error":
            click.secho(f"Error: {resolution_result['message']}", fg="red")
            sys.exit(1)

        # Display fixes applied
        click.secho(f"✓ Total fixes applied: {resolution_result['total_fixes']}", fg="green", bold=True)
        for fix in resolution_result["fixes_applied"]:
            click.secho(f"  {fix}", fg="green")

        # Step 3: Validate fixed manifest
        click.echo("\n✅ Step 3: Validating fixed manifest...")
        click.echo("-" * 70)

        fixed_manifest = resolution_result["fixed_manifest"]
        validation_result = agent.validate_manifest_content(fixed_manifest)

        if validation_result["status"] == "valid":
            click.secho("✓ Fixed manifest is now valid!", fg="green", bold=True)
        else:
            click.secho("⚠ Fixed manifest still has issues:", fg="yellow")
            for error in validation_result["errors"]:
                click.secho(f"  - {error}", fg="yellow")

        # Summary
        click.echo("\n" + "=" * 70)
        click.secho("✨ RESOLUTION COMPLETE ✨", fg="cyan", bold=True)
        click.echo("=" * 70)

        if output:
            click.secho(f"✓ Fixed manifest saved to: {output}", fg="green")
            click.echo("\nTo use the fixed manifest:")
            click.echo(f"  kubectl apply -f {output}")
        else:
            click.echo("\nFixed manifest (YAML):")
            click.echo("-" * 70)
            import yaml
            click.echo(yaml.dump(fixed_manifest, default_flow_style=False))

    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


@cli.command()
@click.argument("manifest_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file for fixed manifest (optional)",
)
def auto_fix(manifest_file, output):
    """Automatically detect, resolve, and validate in one command."""
    agent = KubeAegisAgent()

    click.echo(f"🚀 Auto-fixing manifest: {manifest_file}")
    click.echo("=" * 70)

    try:
        result = agent.auto_resolve_and_validate(manifest_file)

        if result.get("status") == "error":
            click.secho(f"Error: {result['message']}", fg="red")
            sys.exit(1)

        # Display resolution details
        resolution = result["resolution"]
        click.secho(f"✓ Manifest Kind: {resolution['manifest_kind']}", fg="cyan")
        click.secho(f"✓ Fixes Applied: {resolution['total_fixes']}", fg="green", bold=True)

        for fix in resolution["fixes_applied"]:
            click.secho(f"  {fix}", fg="green")

        # Display validation results
        validation = result["validation"]
        click.echo("\n" + "-" * 70)
        click.echo("Final Validation:")
        click.echo("-" * 70)

        if validation["status"] == "valid":
            click.secho("✓ Manifest is now VALID!", fg="green", bold=True)
        else:
            click.secho("⚠ Issues remain:", fg="yellow")
            for error in validation["errors"]:
                click.secho(f"  - {error}", fg="yellow")

        click.echo("\n" + "=" * 70)
        click.secho("✨ AUTO-FIX COMPLETE ✨", fg="cyan", bold=True)
        click.echo("=" * 70)

        if output:
            fixed_manifest = resolution["fixed_manifest"]
            import yaml
            with open(output, "w") as f:
                yaml.dump(fixed_manifest, f, default_flow_style=False)
            click.secho(f"✓ Fixed manifest saved to: {output}", fg="green")
            click.echo(f"\nDeploy with: kubectl apply -f {output}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
