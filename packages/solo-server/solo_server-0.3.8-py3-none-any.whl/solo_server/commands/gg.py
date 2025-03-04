#!/usr/bin/env python3
"""
solo_pro_helm.py

Generate and deploy a multi-container solution using Helm to manage manifested dockers via KubeAI.

This script performs the following steps:
  1. Adds and updates the KubeAI Helm repository.
  2. Installs KubeAI and waits for all components to be ready.
  3. Creates a default models configuration file (kubeai-models.yaml) if one is not provided.
  4. Installs predefined models via Helm.
  5. Optionally sets up a port-forward to the bundled chat UI.

Usage Examples:
  $ ./solo_pro_helm.py "Deploy a blueprint for PDF to Podvast conversion" --models-file my-models.yaml
  $ ./solo_pro_helm.py "Deploy a digital human blueprint with facial recognition and NLP" --no-port-forward
"""

import os
import subprocess
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_command(command: str):
    console.print(f"[cyan]Executing:[/] {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        console.print(f"[red]Command failed: {command}[/red]")
        raise typer.Exit(code=1)

def create_default_models_file(models_file: str):
    default_content = """catalog:
  deepseek-r1-1.5b-cpu:
    enabled: true
    features: [TextGeneration]
    url: 'ollama://deepseek-r1:1.5b'
    engine: OLlama
    minReplicas: 1
    resourceProfile: 'cpu:1'
  qwen2-500m-cpu:
    enabled: true
  nomic-embed-text-cpu:
    enabled: true
"""
    with open(models_file, "w") as f:
        f.write(default_content)
    console.print(f"[green]Default models file created at {models_file}[/green]")

def main(
    blueprint: str = typer.Argument(..., help="A brief description of the blueprint (e.g. 'PDF to Podvast conversion' or 'Digital Human')"),
    models_file: str = typer.Option("kubeai-models.yaml", "--models-file", "-f", help="Path to the models configuration file"),
    no_port_forward: bool = typer.Option(False, "--no-port-forward", help="Skip setting up port-forward to access the web UI"),
    timeout: str = typer.Option("10m", "--timeout", help="Timeout for helm install kubeai")
):
    console.print(Panel.fit(f"Deploying blueprint: {blueprint}", title="[bold cyan]Solo Pro Helm[/]"))

    # Step 1: Add and update the KubeAI Helm repository.
    run_command("helm repo add kubeai https://www.kubeai.org")
    run_command("helm repo update")

    # Step 2: Install KubeAI and wait for all components to be ready.
    console.print(Panel.fit("Installing KubeAI. This may take up to 10 minutes...", title="[bold magenta]KubeAI Installation[/]"))
    run_command(f"helm install kubeai kubeai/kubeai --wait --timeout {timeout}")

    # Step 3: Create models configuration file if it doesn't exist.
    if not os.path.exists(models_file):
        create_default_models_file(models_file)
    else:
        console.print(f"[yellow]Using existing models file: {models_file}[/yellow]")

    # (Optional) Here you could extend the script to customize the models file based on the blueprint.
    # For now, we use the default content.

    # Step 4: Install predefined models.
    console.print(Panel.fit("Installing predefined models via Helm", title="[bold magenta]Model Installation[/]"))
    run_command(f"helm install kubeai-models kubeai/models -f {models_file}")

    console.print(Panel.fit("KubeAI and models installed successfully!\nMonitor pod status with:\n  kubectl get pods --watch", title="[bold green]Deployment Complete[/]"))

    # Step 5: Optionally set up port-forward to the bundled chat UI.
    if not no_port_forward:
        console.print("Setting up port-forward to access the KubeAI web UI at http://localhost:8000")
        console.print("Press Ctrl+C to terminate the port-forward when finished.")
        try:
            run_command("kubectl port-forward svc/open-webui 8000:80")
        except KeyboardInterrupt:
            console.print("[yellow]Port-forward terminated by user.[/yellow]")
    else:
        console.print("[yellow]Port-forward skipped as per option.[/yellow]")

    console.print(Panel.fit("KubeAI deployment and model installation complete.\nTo interact with models, open your browser to http://localhost:8000", title="[bold cyan]Solo Pro Helm Complete[/]"))

if __name__ == "__main__":
    typer.run(main)
