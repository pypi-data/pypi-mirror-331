#!/usr/bin/env python3
"""
Command-line interface for py-HiveFlow.
"""
import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, List

import click
from jinja2 import Environment, FileSystemLoader

from hiveflow.version import __version__

logger = logging.getLogger(__name__)

# Configure templates location
TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


@click.group()
@click.version_option(version=__version__, prog_name="py-HiveFlow")
def main():
    """py-HiveFlow: A distributed producer/consumer framework for Python."""
    pass


@main.command("init")
@click.argument("project_name")
@click.option("--docker/--no-docker", default=True, help="Include Docker configuration")
def init_project(project_name: str, docker: bool):
    """Initialize a new py-HiveFlow project."""
    # Create project directory
    project_path = Path(project_name)

    # check project name is not path
    if "/" in project_name or "\\" in project_name:
        click.echo("WARNING: Project name should not be a string without path.")
        project_name = project_name.split("/")[-1]
        if click.confirm(f"Use '{project_name}' for project name?", default=False) == False:
            return 

    if project_path.exists():
        # Check if directory is empty
        if any(project_path.iterdir()):
            # Directory exists and has content
            if click.confirm(f"Directory '{project_name}' already exists and contains files. Overwrite?", default=False):
                # Empty the directory instead of removing and recreating it
                for item in project_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            else:
                click.echo("Aborting.")
                return
    else:
        # Create new directory
        project_path.mkdir(parents=True)
    
    # Create initial files
    create_project_files(project_path, project_name, docker)
    
    click.echo(f"Successfully created '{project_name}' project.")
    click.echo(f"\nTo start working with your project:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  pip install -e .")
    
    if docker:
        click.echo(f"\nTo run using Docker:")
        click.echo(f"  docker-compose -f docker/docker-compose.yml up -d")


@main.command("create")
@click.argument("component_type", type=click.Choice(["worker", "task", "project"]))
@click.argument("name")
@click.option("--directory", "-d", default=".", help="Project directory")
def create_component(component_type: str, name: str, directory: str):
    """Create a new component (worker or task)."""
    dir_path = Path(directory)
    
    if not (dir_path / "src").exists():
        click.echo("Error: Not in a py-HiveFlow project directory. Run 'hiveflow init' first.")
        return
    
    if component_type == "worker":
        create_worker(dir_path, name)
    elif component_type == "task":
        create_task(dir_path, name)
    elif component_type == "project":
        click.echo("Creating a new project. Use 'hiveflow init' instead.")
        return


@main.command("start")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--config", "-c", default="config.json", help="Configuration file")
def start(host: str, port: int, config: str):
    """Start the py-HiveFlow system."""
    click.echo(f"Starting py-HiveFlow on {host}:{port}...")
    # TODO: Implement actual startup logic
    click.echo("Not yet implemented. Use docker-compose instead.")


def create_project_files(project_path: Path, project_name: str, include_docker: bool):
    """Create initial project files."""
    # Create directory structure - using exist_ok=True to handle existing directories
    src_dir = project_path / "src"
    tests_dir = project_path / "tests"
    docs_dir = project_path / "docs"
    
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create setup.py
    template = env.get_template("setup.py.template")
    setup_content = template.render(project_name=project_name)
    with open(project_path / "setup.py", "w") as f:
        f.write(setup_content)
    
    # Create pyproject.toml
    template = env.get_template("pyproject.toml.template")
    pyproject_content = template.render()
    with open(project_path / "pyproject.toml", "w") as f:
        f.write(pyproject_content)
    
    # Create README.md
    template = env.get_template("README.md.template")
    readme_content = template.render(project_name=project_name)
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)
    
    # Create main package
    package_name = project_name.replace("-", "_")
    package_path = src_dir / package_name
    package_path.mkdir(parents=True, exist_ok=True)

    print(f"Creating package at {package_path}")
    
    # Create package init file
    with open(package_path / "__init__.py", "w") as f:
        f.write(f'"""Main package for {project_name}."""\n\n__version__ = "0.1.0"\n')
    
    # Create basic structure
    core_dir = package_path / "core"
    workers_dir = package_path / "workers" 
    tasks_dir = package_path / "tasks"
    
    core_dir.mkdir(exist_ok=True)
    workers_dir.mkdir(exist_ok=True)
    tasks_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files
    with open(core_dir / "__init__.py", "w") as f:
        f.write('"""Core components for the project."""\n')
    
    with open(workers_dir / "__init__.py", "w") as f:
        f.write('"""Worker implementations."""\n')
    
    with open(tasks_dir / "__init__.py", "w") as f:
        f.write('"""Task definitions."""\n')
    
    # Create Docker files if requested
    if include_docker:
        docker_path = project_path / "docker"
        docker_path.mkdir()
        
        # Create docker-compose.yml
        compose_template = env.get_template("docker-compose.yml.template")
        compose_content = compose_template.render(project_name=project_name)
        with open(docker_path / "docker-compose.yml", "w") as f:
            f.write(compose_content)
        
        # Create development compose file
        dev_compose_template = env.get_template("docker-compose.dev.yml.template")
        dev_compose_content = dev_compose_template.render(project_name=project_name)
        with open(docker_path / "docker-compose.dev.yml", "w") as f:
            f.write(dev_compose_content)
        
        # Create coordinator Dockerfile
        coordinator_path = docker_path / "coordinator"
        coordinator_path.mkdir()
        dockerfile_template = env.get_template("Dockerfile.coordinator.template")
        dockerfile_content = dockerfile_template.render(project_name=project_name)
        with open(coordinator_path / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Create worker Dockerfile
        worker_path = docker_path / "worker"
        worker_path.mkdir()
        dockerfile_template = env.get_template("Dockerfile.worker.template")
        dockerfile_content = dockerfile_template.render(project_name=project_name)
        with open(worker_path / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Create monitor Dockerfile
        monitor_path = docker_path / "monitor"
        monitor_path.mkdir()
        dockerfile_template = env.get_template("Dockerfile.monitor.template")
        dockerfile_content = dockerfile_template.render(project_name=project_name)
        with open(monitor_path / "Dockerfile", "w") as f:
            f.write(dockerfile_content)


def create_worker(project_dir: Path, worker_name: str):
    """Create a new worker component."""
    # Find the package name
    src_dir = project_dir / "src"
    package_dirs = [d for d in src_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists()]
    
    if not package_dirs:
        click.echo("Error: Cannot find Python package in src/ directory.")
        return
    
    package_dir = package_dirs[0]
    package_name = package_dir.name
    
    # Create worker file
    worker_path = package_dir / "workers"
    if not worker_path.exists():
        worker_path.mkdir()
        with open(worker_path / "__init__.py", "w") as f:
            f.write('"""Worker implementations."""\n')
    
    worker_file_name = f"{worker_name.lower().replace('-', '_')}_worker.py"
    worker_class_name = "".join(word.capitalize() for word in worker_name.replace('-', '_').split('_')) + "Worker"
    
    template = env.get_template("custom_worker.py.template")
    worker_content = template.render(
        worker_class_name=worker_class_name,
        worker_name=worker_name,
        package_name=package_name
    )
    
    with open(worker_path / worker_file_name, "w") as f:
        f.write(worker_content)
    
    # Update __init__.py to import the new worker
    with open(worker_path / "__init__.py", "a") as f:
        f.write(f"\nfrom {package_name}.workers.{worker_file_name[:-3]} import {worker_class_name}\n")
        f.write(f"__all__ = ['{worker_class_name}']\n")
    
    click.echo(f"Created new worker: {worker_class_name}")
    click.echo(f"File location: {worker_path / worker_file_name}")


def create_task(project_dir: Path, task_name: str):
    """Create a new task component."""
    # Find the package name
    src_dir = project_dir / "src"
    package_dirs = [d for d in src_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists()]
    
    if not package_dirs:
        click.echo("Error: Cannot find Python package in src/ directory.")
        return
    
    package_dir = package_dirs[0]
    package_name = package_dir.name
    
    # Create task file
    task_path = package_dir / "tasks"
    if not task_path.exists():
        task_path.mkdir()
        with open(task_path / "__init__.py", "w") as f:
            f.write('"""Task definitions."""\n')
    
    task_file_name = f"{task_name.lower().replace('-', '_')}_task.py"
    task_class_name = "".join(word.capitalize() for word in task_name.replace('-', '_').split('_')) + "Task"
    
    template = env.get_template("custom_task.py.template")
    task_content = template.render(
        task_class_name=task_class_name,
        task_name=task_name,
        package_name=package_name
    )
    
    with open(task_path / task_file_name, "w") as f:
        f.write(task_content)
    
    # Update __init__.py to import the new task
    with open(task_path / "__init__.py", "a") as f:
        f.write(f"\nfrom {package_name}.tasks.{task_file_name[:-3]} import {task_class_name}\n")
        f.write(f"__all__ = ['{task_class_name}']\n")
    
    click.echo(f"Created new task: {task_class_name}")
    click.echo(f"File location: {task_path / task_file_name}")


if __name__ == "__main__":
    main()
