import shutil
import click
import webbrowser
import os
import json
import configparser
from pathlib import Path
from fnmatch import fnmatch
import tomllib
import sys
import re

import requests
from almanak import Almanak, __version__
import ast
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        click.echo("Loaded environment variables from .env file")


def load_api_key():
    """Loads the API key from the config file."""
    # Load environment variables first

    config_dir = click.get_app_dir("almanak")
    config_file = os.path.join(config_dir, "config.ini")

    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)
        env = os.environ.get("ALMANAK_ENV", "prod")
        if env in config:
            return config[env].get("api_key")

    return None


def initialize_client():
    """Initialize the Almanak client using the API key."""
    api_key = load_api_key()

    if not api_key:
        raise Exception("No API key found. Please run 'almanak auth' first.")

    return Almanak(api_key=api_key)


def save_api_key(api_key):
    """Saves the API key to the config file."""
    config_dir = click.get_app_dir("almanak")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.ini")

    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)

    env = os.environ.get("ALMANAK_ENV", "prod")
    if env not in config:
        config[env] = {}

    config[env]["api_key"] = api_key

    with open(config_file, "w") as f:
        config.write(f)


def format_output(
    status: str = None, title=None, key_value_pairs=None, items=None, delimiter=True
):
    """
    Formats and prints a title, a dictionary of key-value pairs, or a list of items with consistent formatting.

    :param status: Status of the response (success, error, info).
    :param title: The section title to display (e.g., "Available Strategies").
    :param key_value_pairs: A dictionary of key-value pairs to display in a formatted manner.
    :param items: A list of items to display with numbering.
    :param delimiter: Whether to print a delimiter (separator line) around the content.
    """
    output = []
    if delimiter:
        output.append("=========================================")

    if status:
        output.append(f"[{status.upper()}]")

    if title:
        output.append(title)
        output.append("-----------------------------------------")

    if key_value_pairs:
        for key, value in key_value_pairs.items():
            output.append(f"{key:<18}: {value}")

    if items:
        for i, item in enumerate(items, start=1):
            output.append(f"{i}. {item}")

    if delimiter:
        output.append("=========================================")

    click.echo("\n".join(output))


@click.group()
@click.version_option(__version__, prog_name="almanak")
def cli():
    """Almanak CLI for managing strategies.

    Available Commands:
      strat     Commands for managing strategies
      auth      Authenticate the Almanak CLI
    """
    load_environment()

@cli.group()
def strat():
    """Commands for managing strategies.

    Commands:
      list
       on the Almanak platform
      describe  Retrieve details of a strategy
      validate  Validate a strategy configuration
      upload    Upload a new strategy version"""
    if click.get_current_context().invoked_subcommand is None:
        click.echo(click.get_current_context().get_help())


@cli.command()
def auth():
    """Authenticate the Almanak CLI"""

    env = os.environ.get("ALMANAK_ENV", "prod")

    match env:
        case "prod":
            url = "https://app.almanak.co/settings/api-keys"
        case "stage":
            url = "https://stage.almanak.co/settings/api-keys"
        case _:
            click.echo(
                "Environment variable ALMANAK_ENV has an invalid value. Please set it to 'prod' or 'stage'."
            )
            return

    click.echo(f"Opening {url} in your default browser...")
    webbrowser.open(url)

    click.echo(f"Authenticating against {env.upper()} environment")

    api_key = click.prompt("Please enter your API key", hide_input=True)

    try:
        Almanak(api_key=api_key, _env=env)
        format_output(
            status="success",
            title="API Key Validation",
            key_value_pairs={"Message": "API key validated successfully."},
        )
    except Exception as e:
        format_output(
            status="error",
            title="API Key Validation Failed",
            key_value_pairs={"Error": str(e)},
        )
        return

    save_api_key(api_key)
    format_output(
        status="success",
        title="API Key Stored",
        key_value_pairs={
            "Message": f"API key for {env.upper()} environment stored successfully. You can now use the Almanak CLI.",
            "Environment": env.upper(),
        },
    )


@strat.command("list")
def list_strategies():
    """List all available strategies on the Almanak platform."""
    try:
        client = initialize_client()

        artifacts_list = client.library.strategies.list(limit=10, offset=0)

        if not artifacts_list:
            format_output(status="info", title="No Strategies Found")
            return

        format_output(
            status="success",
            title="Available Strategies:",
            items=[f"{artifact.name} (ID: {artifact.id})" for artifact in artifacts_list],
        )

    except Exception as e:
        format_output(
            status="error",
            title="Failed to Fetch Strategies",
            key_value_pairs={"Error": str(e)},
        )


@strat.command("describe")
@click.option(
    "--strategy-name", required=True, help="The name of the strategy to retrieve."
)
@click.option(
    "--version",
    help="Specific version of the strategy to retrieve. If not provided, returns all versions.",
)
def get_strategy(strategy_name, version):
    """Retrieve the details of a strategy. If version is specified, retrieves that specific version."""
    try:
        client = initialize_client()

        if version:
            # Get specific version
            result = client.library.strategies.versions.retrieve(strategy_name, version)
            if not result or not result.data:
                format_output(
                    status="error",
                    title=f"Strategy '{strategy_name}' version '{version}' not found",
                )
                return

            version_info = result.data[0]  # Get the first item from data list

            # Format version-specific output
            format_output(
                status="success",
                title=f"Details for Strategy: {strategy_name} (Version {version})",
                key_value_pairs={
                    "Version": version_info.name,
                    "Author": version_info.author,
                    "Created At": version_info.date_created,
                    "Description": version_info.description
                    or "No description available",
                    "Is Public": "Yes" if version_info.is_public else "No",
                    "Metadata": (
                        json.dumps(version_info.metadata, indent=2)
                        if version_info.metadata
                        else "No metadata"
                    ),
                },
            )
        else:
            # Get strategy info and all versions
            strategy_result = client.library.strategies.retrieve(strategy_name)
            versions_result = client.library.strategies.versions.list(strategy_name)

            if not strategy_result or not strategy_result.data:
                format_output(
                    status="error", title=f"Strategy '{strategy_name}' not found"
                )
                return

            strategy = strategy_result.data[0]

            # Prepare versions information
            versions_info = []
            for v in versions_result:
                versions_info.append(
                    f"Version: {v.name}\n"
                    f"   Author: {v.author}\n"
                    f"   Created: {v.date_created}\n"
                    f"   Description: {v.description or 'No description available'}\n"
                    f"   Public: {'Yes' if v.is_public else 'No'}\n"
                    f"   Metadata: {json.dumps(v.metadata, indent=2) if v.metadata else 'No metadata'}"
                )

            format_output(
                status="success",
                title=f"Details for Strategy: {strategy.name}",
                key_value_pairs={
                    "Author": strategy.author,
                    "Description": strategy.description or "No description available",
                    "Public": "Yes" if strategy.is_public else "No",
                    "Created At": strategy.date_created,
                    "Latest Version": strategy.latest_version_artifact.name,
                    "Latest Version Metadata": (
                        json.dumps(strategy.latest_version_artifact.metadata, indent=2)
                        if strategy.latest_version_artifact.metadata
                        else "No metadata"
                    ),
                },
                items=versions_info,  # Add all versions as a list
            )

    except Exception as e:
        format_output(
            status="error",
            title="Failed to retrieve strategy",
            key_value_pairs={"Error": str(e)},
        )


def get_ignore_patterns(working_dir, ignore_file=None):
    """
    Get ignore patterns from .almanakignore or .gitignore files.

    Args:
        working_dir (str): The working directory path
        ignore_file (str, optional): Custom ignore file path

    Returns:
        list: List of ignore patterns
    """
    ignore_patterns = []

    # Priority: custom ignore file > .almanakignore > .gitignore
    ignore_files = [
        ignore_file,
        os.path.join(working_dir, ".almanakignore"),
        os.path.join(working_dir, ".gitignore"),
    ]

    for file_path in ignore_files:
        if file_path and os.path.isfile(file_path):
            with open(file_path, "r") as f:
                patterns = [
                    line.strip()
                    for line in f.readlines()
                    if line.strip() and not line.startswith("#")
                ]
                ignore_patterns.extend(patterns)
            break  # Use first found ignore file

    # Add default patterns
    default_patterns = [
        ".git/",
        "__pycache__/",
        "*.pyc",
        ".DS_Store",
        ".env",
        ".venv/",
        "venv/",
        ".idea/",
        ".vscode/",
    ]
    ignore_patterns.extend(default_patterns)

    return ignore_patterns


def should_ignore_file(file_path, ignore_patterns):
    """
    Check if a file should be ignored based on ignore patterns.

    Args:
        file_path (str): The file path to check
        ignore_patterns (list): List of ignore patterns

    Returns:
        bool: True if file should be ignored, False otherwise
    """
    file_path = Path(file_path)
    relative_path = str(file_path.as_posix())

    for pattern in ignore_patterns:
        if pattern.endswith("/"):
            # Directory pattern
            if any(parent.name == pattern[:-1] for parent in file_path.parents):
                return True
        elif fnmatch(relative_path, pattern) or fnmatch(file_path.name, pattern):
            return True
    return False


def extract_strategy_parameters_static(
    file_path: str, strategy_class: str
) -> Optional[Dict[str, Any]]:
    """
    Extract parameter information from the strategy class using static code analysis.

    Args:
        file_path: Path to the strategy file
        strategy_class: Name of the strategy class to analyze

    Returns:
        Dictionary containing parameter information or None if class not found
    """
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == strategy_class:
                # Find the __init__ method
                init_method = next(
                    (
                        n
                        for n in node.body
                        if isinstance(n, ast.FunctionDef) and n.name == "__init__"
                    ),
                    None,
                )

                if not init_method:
                    return {}

                strategy_parameters = {}

                # Skip the first argument (self)
                for arg in init_method.args.args[1:]:
                    param_info = {
                        "optional": False,
                    }

                    # Get type annotation if it exists
                    if arg.annotation:
                        param_info["type"] = ast.unparse(arg.annotation)

                    # Check for default value
                    arg_idx = init_method.args.args.index(arg)
                    defaults_idx = arg_idx - (
                        len(init_method.args.args) - len(init_method.args.defaults)
                    )
                    if defaults_idx >= 0:
                        default_value = init_method.args.defaults[defaults_idx]
                        param_info["optional"] = True
                        try:
                            param_info["default"] = ast.literal_eval(default_value)
                        except ValueError:
                            # If we can't evaluate the default value, store it as a string
                            param_info["default"] = ast.unparse(default_value)

                    strategy_parameters[arg.arg] = param_info

                return strategy_parameters

        return None
    except Exception as e:
        raise Exception(f"Failed to extract strategy parameters: {str(e)}")


def validate_strategy_preset(preset: dict, working_dir: Path):
    preset_title = preset.get("title")
    if not preset_title:
        raise ValueError("title not found in preset")
    if not preset.get("description"):
        raise ValueError("description not found in preset")
    if not preset.get("chain"):
        raise ValueError("chain not found in preset")

    strategy_config_path_parts = Path(preset["config"]).parts
    strategy_config_path = working_dir / Path(*strategy_config_path_parts)
    if not strategy_config_path.exists():
        raise ValueError(
            f"strategy config path {strategy_config_path} does not exist for preset {preset_title}"
        )
    try:
        config_data = json.load(open(strategy_config_path))
        if not config_data:
            raise ValueError(
                f"strategy config file {strategy_config_path} is empty for preset {preset_title}"
            )
    except Exception as e:
        raise ValueError(
            f"strategy config file {strategy_config_path} is invalid for preset {preset_title}"
        ) from e
    print(f"Validated strategy config file exists for preset {preset_title}")

    permissions_path_parts = Path(preset["permissions"]).parts
    permissions_path = working_dir / Path(*permissions_path_parts)
    if not permissions_path.exists():
        raise ValueError(
            f"permissions path {permissions_path} does not exist for preset {preset_title}"
        )
    print(f"Validated permissions file exists for preset {preset_title}")

    env_path_parts = Path(preset["env"]).parts
    env_path = working_dir / Path(*env_path_parts)
    if not env_path.exists():
        raise ValueError(
            f"env path {env_path} does not exist for preset {preset_title}"
        )
    print(f"Validated env file exists for preset {preset_title}")


def validate_pyproject_contents(pyproject_toml: Path, working_dir: str) -> bool:
    pyproject_data = tomllib.load(open(pyproject_toml, "rb"))
    detected_package_name = Path(working_dir).resolve().name
    if detected_package_name != pyproject_data["project"]["name"]:
        format_output(
            status="error",
            title="package name in pyproject.toml does not match working directory name",
            key_value_pairs={
                "Error": f"package name in pyproject.toml: {pyproject_data['project']['name']}",
                "Working Directory": working_dir,
            },
        )
        return
    strategy_presets = pyproject_data["tool"]["presets"]
    for strategy_preset_name, strategy_preset in strategy_presets.items():
        try:
            validate_strategy_preset(strategy_preset, Path(working_dir))
        except Exception as e:
            format_output(
                status="error",
                title=f"Invalid Strategy Preset: {strategy_preset_name}",
                key_value_pairs={
                    "Error": str(e),
                    "Preset Name": strategy_preset_name,
                },
            )
            return False

    return True


@strat.command("validate")
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory containing the strategy files. Defaults to the current directory.",
)
@click.option(
    "--strategy-entry-file",
    default="strategy.py",
    help="Name of the strategy entry file. Defaults to 'strategy.py'.",
)
@click.option(
    "--config-file",
    # type=click.Path(exists=True),
    help="Path to custom config file. Defaults to config.json in working directory.",
)
@click.option(
    "--strategy-class",
    default="Strategy",
    help="Name of the strategy class to look for. Defaults to 'Strategy'.",
)
@click.option(
    "--ignore-file",
    type=click.Path(exists=True),
    help="Custom ignore file path. Defaults to .almanakignore or .gitignore if present.",
)
@click.option(
    "--pip-dependency-file",
    type=click.Path(exists=True),
    help="Path to pip dependency file. Defaults to searching for requirements.txt or requirements.pip.",
)
def validate_strategy(
    working_dir,
    strategy_entry_file,
    config_file,
    strategy_class,
    ignore_file,
    pip_dependency_file,
):
    """Validate the strategy file and configuration."""

    file_path = os.path.join(working_dir, strategy_entry_file)

    # Step 1: Check if the strategy file exists
    if not os.path.isfile(file_path):
        format_output(
            status="error",
            title="File Not Found",
            key_value_pairs={
                "Working Directory": working_dir,
                "Strategy Entry File": strategy_entry_file,
            },
        )
        return None

    try:
        # Get ignore patterns using the provided ignore_file
        ignore_patterns = get_ignore_patterns(working_dir, ignore_file)

        # Get files recursively
        files_to_upload = get_files_to_upload(working_dir, ignore_patterns)

        # Check for pip dependency file
        if pip_dependency_file:
            if os.path.isfile(pip_dependency_file):
                pip_dependency_file = os.path.basename(pip_dependency_file)
            else:
                format_output(
                    status="error",
                    title="Pip Dependency File Not Found",
                    key_value_pairs={
                        "Error": f"Specified pip dependency file '{pip_dependency_file}' not found",
                    },
                )
                return None
        else:
            # Default behavior: look for requirements.txt or requirements.pip
            pip_files = ["requirements.txt", "requirements.pip"]
            pip_dependency_file = next(
                (f for f in pip_files if os.path.isfile(os.path.join(working_dir, f))),
                "",
            )

        """validate pyproject.toml exists"""

        pyproject_toml_path = Path(working_dir) / "pyproject.toml"
        if not pyproject_toml_path.exists():
            format_output(
                status="error",
                title="pyproject.toml Not Found",
                key_value_pairs={
                    "Error": f"pyproject.toml not found in the working directory",
                },
            )
            return

        pyproject_data = tomllib.load(open(pyproject_toml_path, "rb"))
        is_pyproject_toml_valid = validate_pyproject_contents(
            pyproject_toml_path, working_dir
        )
        if not is_pyproject_toml_valid:
            return

        validation_result = {
            # "strategy_name": strategy_name,
            # "safe_wallets_permission": safe_wallets_permission,
            "pip_dependency_file": pip_dependency_file,
            "files_to_upload": files_to_upload,
            # "strategy_parameters": strategy_parameters,
            # "strategy_required_env": config.get(
            #     "strategy_required_env", {}
            # ),  # Renamed from strategy_env_secrets
            "strategy_class_name": strategy_class,  # Add this line
            # "config_file_path": config_file or "config.json",  # Add this line
            "strategy_presets": pyproject_data,
            "pyproject_data": pyproject_data,
        }

        format_output(
            status="success",
            title="Strategy Validated Successfully",
        )

        return validation_result

    except Exception as e:
        format_output(
            status="error",
            title="Validation Error",
            key_value_pairs={"Error": str(e)},
        )
        return None


@strat.command("push")
@click.option(
    "--strategy-name",
    help="The name of the strategy. If not provided, it will be read from the STRATEGY_NAME class attribute.",
)
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory containing the strategy files. Defaults to the current directory.",
)
@click.option(
    "--strategy-entry-file",
    default="strategy.py",
    help="Name of the strategy entry file. Defaults to 'strategy.py'.",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to custom config file. Defaults to config.json in working directory.",
)
@click.option(
    "--strategy-class",
    default="Strategy",
    help="Name of the strategy class to look for. Defaults to 'Strategy'.",
)
@click.option(
    "--ignore-file",
    type=click.Path(exists=True),
    help="Custom ignore file path. Defaults to .almanakignore or .gitignore if present.",
)
@click.option(
    "--pip-dependency-file",
    type=click.Path(exists=True),
    help="Path to pip dependency file. Defaults to searching for requirements.txt or requirements.pip.",
)
def push_strategy(
    strategy_name,
    working_dir,
    strategy_entry_file,
    config_file,
    strategy_class,
    ignore_file,
    pip_dependency_file,
):
    """Push a new version of your strategy."""

    try:
        # First, validate the strategy
        ctx = click.get_current_context()
        validation_result = ctx.invoke(
            validate_strategy,
            working_dir=working_dir,
            strategy_entry_file=strategy_entry_file,
            config_file=config_file,
            strategy_class=strategy_class,
            ignore_file=ignore_file,
            pip_dependency_file=pip_dependency_file,
        )

        if not validation_result:
            click.echo("Push aborted due to validation failure.")
            return

        # strategy_name = strategy_name or validation_result.get("strategy_name")
        # if not strategy_name:
        #     raise click.UsageError(
        #         "Strategy name must be provided either via --strategy-name option or as a STRATEGY_NAME class attribute."
        #     )

        # Get description from config if not provided via CLI
        # strategy_description = description or "No description provided"
        strategy_description = validation_result["pyproject_data"]["project"][
            "description"
        ]
        strategy_presets = validation_result.get("strategy_presets")

        safe_wallets_permission = validation_result.get("safe_wallets_permission", [])
        strategy_wallets_requirements = validation_result.get(
            "strategy_wallets_requirements", "{}"
        )
        strategy_parameters = validation_result.get("strategy_parameters", {})

        # Use the pip file from validation if not provided
        pip = validation_result.get("pip_dependency_file")

        # Use the filtered files from validation
        file_paths = [
            os.path.join(working_dir, f) for f in validation_result["files_to_upload"]
        ]

        # Initialize client
        client = initialize_client()

        click.echo(f"Pushing strategy '{strategy_name}'...")

        # Parse JSON strings to dicts
        strategy_wallets_requirements_dict = json.loads(strategy_wallets_requirements)

        # Get relative paths for config and strategy files
        working_dir_path = Path(working_dir)
        # config_path = Path(
        #     config_file if config_file else os.path.join(working_dir, "config.json")
        # )
        # relative_config_path = str(config_path.relative_to(working_dir_path))
        relative_strategy_path = str(
            Path(os.path.join(working_dir, strategy_entry_file)).relative_to(
                working_dir_path
            )
        )
        metadata = {
            "safe_wallets_permission": safe_wallets_permission,
            "strategy_wallets_requirements": strategy_wallets_requirements_dict,
            "strategy_parameters": strategy_parameters,
            "strategy_class_name": strategy_class,
            "strategy_file_entrypoint": relative_strategy_path,
            # "config_file_path": relative_config_path,
            "strategy_presets": strategy_presets,
        }

        # Check for pip dependency file
        if pip:
            if os.path.isfile(os.path.join(working_dir, pip)):
                metadata["pip_dependency_file"] = pip
            else:
                click.echo(f"Warning: Specified pip dependency file '{pip}' not found.")

        # Check if the strategy exists
        if not client.library.strategies.retrieve(strategy_name).data:
            try:
                client.library.strategies.create(
                    strategy_name=strategy_name, description=strategy_description
                )
            except Exception as e:
                click.echo(
                    f"Error creating strategy '{strategy_name}': {str(e)}, the strategy name already exists",
                    err=True,
                )
                return

        file_paths = [path.removeprefix("./") for path in file_paths]

        pushed_strategy = client.library.strategies.upload_new_version(
            strategy_name=strategy_name, files=file_paths
        )
        pushed_strategy_root_uri = pushed_strategy.rootUri

        metadata["uri"] = pushed_strategy_root_uri

        updates = {
            "metadata": metadata,
            "uri": pushed_strategy_root_uri,
            "description": strategy_description,
        }

        # Set metadata by updating the strategy metadata field
        client.library.strategies.versions.update(
            strategy_name=strategy_name,
            version=pushed_strategy.version,
            updates=updates,
        )

        try:
            # Trigger scan
            resp = client.strategy.trigger_scan(
                artifact_version_id=pushed_strategy.versionId
            )
            if not resp["success"]:
                click.echo(f"Failed to trigger the security scan due to {resp.message}")
            click.echo("Triggered security scan successfully")
        except Exception as e:
            format_output(
            status="error",
            title=f"Failed to trigger security scan for strategy '{strategy_name} but the strategy was pushed successfully",
            key_value_pairs={"Error": str(e)},
        )


        format_output(
            status="success",
            title=f"Pushed strategy '{strategy_name}' successfully with version '{pushed_strategy.version}'.",
        )

    except click.UsageError as e:
        click.echo(str(e), err=True)
    except json.JSONDecodeError:
        format_output(
            status="error",
            title="Invalid JSON input",
            key_value_pairs={
                "Error": "Please provide valid JSON for safe_wallets_permission and strategy_wallets_requirements."
            },
        )
    except Exception as e:
        format_output(
            status="error",
            title=f"Failed to push strategy '{strategy_name}'",
            key_value_pairs={"Error": str(e)},
        )


# Replace the existing code that gets files_to_upload with this new implementation
def get_files_to_upload(working_dir: str, ignore_patterns: list) -> list:
    """
    Recursively get all files to upload, respecting ignore patterns.
    Skips files without extensions and .gitignore files.

    Args:
        working_dir (str): Working directory path
        ignore_patterns (list): List of ignore patterns

    Returns:
        list: List of relative file paths to upload
    """
    files_to_upload = []
    working_dir_path = Path(working_dir)

    for root, dirs, files in os.walk(working_dir):
        # Remove ignored directories
        dirs[:] = [
            d
            for d in dirs
            if not should_ignore_file(os.path.join(root, d), ignore_patterns)
        ]

        for file in files:
            # Skip files without extensions and .gitignore
            if "." not in file or file == ".gitignore":
                continue

            file_path = os.path.join(root, file)
            if not should_ignore_file(file_path, ignore_patterns):
                # Get path relative to working directory
                relative_path = str(Path(file_path).relative_to(working_dir_path))
                files_to_upload.append(relative_path)

    return files_to_upload


@strat.command()
@click.option(
    "--strategy-id", required=True, help="The id of the strategy to download."
)
@click.option("--version", help="Specific version of the strategy to download.")
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory to download the strategy to. Defaults to the current directory.",
)
def pull(strategy_id: str, version: str, working_dir: str):
    """Downloads your strategy."""
    try:
        client = initialize_client()
        artifacts_list = client.library.strategies.list(limit=10, offset=0)
        if not artifacts_list:
            format_output(status="error", title="No Strategies Found")
            return
        strategy_name = None
        for artifact in artifacts_list:
            if artifact.id == strategy_id:
                strategy_name = artifact.name
                latest_version = artifact.latest_version_artifact.name
                version_id = artifact.latest_version_artifact.id
                break
        if version is not None:
            version_id = client.strategy.get_version_id_by_name(strategy_id, version)
        else:
            version = latest_version

        if strategy_name is None:
            format_output(
                status="error", title=f"Strategy '{strategy_name}' not found"
            )
            return
        click.echo(f"Downloading version: {version}")
        
        client.strategy.download_strategy(strategy_name, strategy_id, version_id, working_dir)

        format_output(
            status="success",
            title="Strategy downloaded successfully",
            key_value_pairs={
                "Destination": working_dir,
                "Version": version,
                "Strategy ID": strategy_id,
                "Strategy Name": strategy_name,
            },
        )

    except Exception as e:
        format_output(
            status="error",
            title="Failed to download the strategy",
            key_value_pairs={"Error": str(e)},
        )


@strat.command()
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory to create a new skeleton strategy. Defaults to the current directory.",
)
def new(working_dir):
    """Create a new skeleton strategy."""
    try:
        full_path = os.path.abspath(working_dir)

        source_dir = os.path.join(os.path.dirname(__file__), "../templates/new")
        strategy_name = click.prompt("Enter a name for your strategy")
        destination_dir = f"{working_dir}/{strategy_name}"
        config_file = os.path.join(destination_dir, "config.json")
        pyproject_file = os.path.join(destination_dir, "pyproject.toml")

        if os.path.exists(source_dir):
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        else:
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")

        # overwrite strategy name in config file
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
            config["name"] = strategy_name
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

        # update project name in pyproject.toml
        if os.path.exists(pyproject_file):
            with open(pyproject_file, "r") as f:
                content = f.read()
            # Replace the project.name line while preserving formatting
            content = re.sub(r'name = ".*"', f'name = "{strategy_name}"', content)
            with open(pyproject_file, "w") as f:
                f.write(content)

        format_output(
            status="success",
            title="New strategy skeleton created successfully",
            key_value_pairs={
                "Destination": full_path,
            },
        )

    except Exception as e:
        format_output(
            status="error",
            title="Failed to create a new strategy",
            key_value_pairs={"Error": str(e)},
        )


@strat.command()
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory to download the example strategy. Defaults to the current directory.",
)
def example(working_dir):
    """Download the example strategy."""
    try:
        full_path = os.path.abspath(working_dir)

        source_dir = os.path.join(
            os.path.dirname(__file__), "../templates/example_strategy"
        )
        destination_dir = f"{working_dir}/example_strategy"
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        else:
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")

        format_output(
            status="success",
            title="Example strategy created successfully",
            key_value_pairs={
                "Destination": full_path,
            },
        )

    except Exception as e:
        format_output(
            status="error",
            title="Failed to create example strategy",
            key_value_pairs={"Error": str(e)},
        )


@strat.command("test")
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=".",
    help="Working directory containing the strategy files. Defaults to the current directory.",
)
@click.option(
    "--preset",
    type=str,
    help="Select the strategy preset to test with.",
)
@click.option(
    "--local-storage",
    type=click.Path(),
    default="./local_storage",
    help="Path to the local storage directory for testing.",
)
@click.option(
    "--clean-restart",
    is_flag=True,
    default=False,
    help="Clean the local storage and restart the strategy.",
)
def test(working_dir, preset, local_storage, clean_restart):
    """Test the strategy locally.
    The following environment variables must be set:
    - ALCHEMY_API_KEY : Your Alchemy API key. This will be used to connect with the node provider
    - PRIVATE_KEY_*: Private keys for the EOA wallets. E.g. PRIVATE_KEY_1
    """

    """Validate required environment variables"""
    os.environ["STORAGE_DIR"] = local_storage

    pyproject_data = tomllib.loads(open(Path(working_dir) / "pyproject.toml").read())

    """copy the current working directory containing the strategy into the framework"""
    strategy_package_name: str = pyproject_data["project"]["name"]
    framework_location: Path = Path(__file__).resolve().parent.parent / "agent_service"
    strategy_location = (
        framework_location / "src" / "strategy" / "strategies" / strategy_package_name
    ).resolve()
    if strategy_location.exists():
        shutil.rmtree(strategy_location)
    shutil.copytree(working_dir, strategy_location.resolve())

    local_storage_directory = Path(local_storage).resolve()

    """nuke local storage directory if clean restart is set"""
    if clean_restart:
        if click.confirm(
            f"Cleaning the local storage directory {local_storage_directory}. Do you confirm?"
        ):
            shutil.rmtree(local_storage_directory, ignore_errors=True)
        else:
            print("Aborting test.")
            sys.exit()

    """Create the local storage directory if it does not exist"""
    if not local_storage_directory.exists():
        local_storage_directory.mkdir(parents=True)

    config_directory = local_storage_directory / "config"

    """Create the config directory in the local storage directory"""
    config_directory.mkdir(exist_ok=True)

    strategy_preset_data = pyproject_data["tool"]["presets"][preset]

    """copy the config file from the preset into the config directory if it does not exist"""
    config_file_location = config_directory / "config.json"
    config_file_in_preset_directory = (
        Path(working_dir)
        / Path(*Path(strategy_preset_data["config"]).parts).resolve()
    )
    shutil.copy(
        config_file_in_preset_directory,
        config_file_location,
    )

    """Get config, environment variables and permissions from the selected preset used in this test run"""
    if strategy_preset_data.get("env"):
        env_file_location = (
            Path(working_dir) / Path(*Path(strategy_preset_data["env"]).parts).resolve()
        )
        load_dotenv(env_file_location)

    sys.path.append(str(framework_location))
    sys.path.append(str(framework_location / "src"))

    """Set environment variables to configure stack for local testing"""
    os.environ.update(
        {
            "ALMANAK_IS_AGENT_DEPLOYMENT": "False",
            "DEBUG_AUTO_UPLOAD_PSTATE_FILE": "True",
            "MAINLOOP_DELAY_SECONDS": "1",
        }
    )

    """set strategy directory"""
    """The below code mints tokens into the user wallet. We will not enable this functionality for now."""
    # from transaction_builder.protocols.uniswap_v3 import abis
    # from almanak.utils.utils import mint

    # erc20 = resources.files(abis) / "erc20_token.json"
    # with open(erc20, "r") as abi_file:
    #     erc20_abi = json.loads(abi_file.read())
    # if "test_tokens" in config:
    #     tokens: list[dict] = config["test_tokens"]
    #     for token in tokens:
    #         mint(
    #             strategy_parameters["web3"],
    #             strategy_parameters["wallet_address"],
    #             token["amount"],
    #             token["name"],
    #             token["address"],
    #             erc20_abi,
    #         )
    """start the stack as per normal"""
    from src.main import super_main

    super_main()


def is_anvil_running(url="http://127.0.0.1:8545"):
    payload = {"jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": 1}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"Anvil is running. Client version: {result['result']}")
                return True
        print(f"Failed to validate Anvil. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Anvil: {e}")

    return False


if __name__ == "__main__":
    cli()
