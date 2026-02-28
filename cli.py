"""
CLI module for kubeAegis AI Agent
Command-line interface for managing and validating Kubernetes manifests
"""

import sys
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


if __name__ == "__main__":
    cli()
