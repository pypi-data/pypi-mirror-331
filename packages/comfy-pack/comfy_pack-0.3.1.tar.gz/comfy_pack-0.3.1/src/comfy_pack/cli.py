import functools
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import cast

import click

from .const import COMFY_PACK_REPO, COMFYUI_MANAGER_REPO, COMFYUI_REPO, WORKSPACE_DIR
from .hash import get_sha256
from .utils import get_self_git_commit


def _ensure_uv() -> None:
    """Ensure uv is installed, raise error if not."""
    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        raise RuntimeError(
            "uv is not installed. Please install it first:\n"
            "curl -LsSf https://astral.sh/uv/install.sh | sh"
        )


@click.group()
def main():
    """comfy-pack CLI"""
    pass


@main.command(
    name="init",
    help="Install latest ComfyUI and comfy-pack custom nodes and create a virtual environment",
)
@click.option(
    "--dir",
    "-d",
    default="ComfyUI",
    help="Target directory to install ComfyUI",
    type=click.Path(file_okay=False),
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity level",
)
def init(dir: str, verbose: int):
    import os

    from rich.console import Console

    console = Console()

    # Check if directory path is valid
    try:
        install_dir = Path(dir).absolute()
        if install_dir.exists() and not install_dir.is_dir():
            console.print(f"[red]Error: {dir} exists but is not a directory[/red]")
            return 1

        # Check if directory is empty or contains ComfyUI
        if install_dir.exists():
            contents = list(install_dir.iterdir())
            if contents and not (install_dir / ".git").exists():
                console.print(
                    f"[red]Error: Directory {dir} is not empty and doesn't appear to be a ComfyUI installation[/red]"
                )
                return 1
    except Exception as e:
        console.print(f"[red]Error: Invalid directory path - {str(e)}[/red]")
        return 1

    # Check git installation
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("[red]Error: git is not installed or not in PATH[/red]")
        return 1

    # Check if we have write permissions
    try:
        if not install_dir.exists():
            install_dir.mkdir(parents=True)
        test_file = install_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError) as e:
        console.print(f"[red]Error: No write permission in {dir} - {str(e)}[/red]")
        return 1

    # Check if Python version is compatible
    if sys.version_info < (3, 8):
        console.print("[red]Error: Python 3.8 or higher is required[/red]")
        return 1

    # Check if uv is installed
    try:
        _ensure_uv()
    except RuntimeError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1

    # Check if enough disk space is available (rough estimate: 2GB)
    try:
        free_space = shutil.disk_usage(install_dir).free
        if free_space < 2 * 1024 * 1024 * 1024:  # 2GB in bytes
            console.print(
                "[yellow]Warning: Less than 2GB free disk space available[/yellow]"
            )
    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not check free disk space - {str(e)}[/yellow]"
        )

    # Clone ComfyUI if not exists
    if not (install_dir / ".git").exists():
        console.print("[green]Cloning ComfyUI...[/green]")
        subprocess.run(
            [
                "git",
                "clone",
                COMFYUI_REPO,
                str(install_dir),
            ],
            check=True,
        )

    # Update ComfyUI
    console.print("[green]Updating ComfyUI...[/green]")
    subprocess.run(
        ["git", "pull"],
        cwd=install_dir,
        check=True,
    )

    # Create and activate venv
    venv_dir = install_dir / ".venv"
    console.print("[green]Creating virtual environment with uv...[/green]")
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    subprocess.run(
        ["uv", "venv", str(venv_dir)],
        check=True,
    )

    # Get python path for future use
    if sys.platform == "win32":
        python = str(venv_dir / "Scripts" / "python.exe")

    else:
        python = str(venv_dir / "bin" / "python")

    # Install requirements with uv
    console.print("[green]Installing ComfyUI requirements with uv...[/green]")
    subprocess.run(
        ["uv", "pip", "install", "pip", "--upgrade"],
        env={
            "VIRTUAL_ENV": str(venv_dir),
            "PATH": str(venv_dir / "bin") + os.pathsep + os.environ["PATH"],
        },
        check=True,
    )
    subprocess.run(
        ["uv", "pip", "install", "-r", str(install_dir / "requirements.txt")],
        env={
            "VIRTUAL_ENV": str(venv_dir),
            "PATH": str(venv_dir / "bin") + os.pathsep + os.environ["PATH"],
        },
        check=True,
    )

    # Install comfy-pack as custom node
    console.print("[green]Installing comfy-pack custom nodes...[/green]")
    custom_nodes_dir = install_dir / "custom_nodes"
    custom_nodes_dir.mkdir(exist_ok=True)

    comfyui_manager_dir = custom_nodes_dir / "ComfyUI-Manager"
    if not (comfyui_manager_dir / ".git").exists():
        # Clone ComfyUI-Manager
        subprocess.run(
            ["git", "clone", COMFYUI_MANAGER_REPO, str(comfyui_manager_dir)],
            check=True,
        )

    comfy_pack_dir = custom_nodes_dir / "comfy-pack"
    if not (comfy_pack_dir / ".git").exists():
        # Clone comfy-pack
        subprocess.run(
            ["git", "clone", COMFY_PACK_REPO, str(comfy_pack_dir)],
            check=True,
        )

    # Update comfy-pack
    subprocess.run(
        ["git", "pull"],
        cwd=comfy_pack_dir,
        check=True,
    )

    # Install comfy-pack requirements
    if (comfy_pack_dir / "requirements.txt").exists():
        subprocess.run(
            [
                python,
                "-m",
                "pip",
                "install",
                "-r",
                str(comfy_pack_dir / "requirements.txt"),
            ],
            check=True,
        )

    version = get_self_git_commit() or "unknown"
    console.print(
        f"\n[green]✓ Installation completed! (comfy-pack version: {version})[/green]"
    )
    console.print(f"ComfyUI directory: {install_dir}")

    console.print(
        "\n[green]Next steps:[/green]\n"
        f"1. cd {dir}\n"
        "2. source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate\n"
        "3. python main.py"
    )


@main.command(
    name="unpack",
    help="Restore the ComfyUI workspace to specified directory",
)
@click.argument("cpack", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--dir",
    "-d",
    default="ComfyUI",
    help="target directory to restore the ComfyUI project",
    type=click.Path(file_okay=False),
)
@click.option(
    "--include-disabled-models",
    default=False,
    type=click.BOOL,
    is_flag=True,
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity level (use multiple times for more verbosity)",
)
def unpack_cmd(cpack: str, dir: str, include_disabled_models: bool, verbose: int):
    from rich.console import Console

    from .package import install

    console = Console()

    install(cpack, dir, verbose=verbose, all_models=include_disabled_models)
    console.print("\n[green]✓ ComfyUI Workspace is restored![/green]")
    console.print(f"{dir}")

    console.print(
        "\n[green] Next steps: [/green]\n"
        "1. Change directory to the restored workspace\n"
        "2. Source the virtual environment by running `source .venv/bin/activate`\n"
        "3. Run the ComfyUI project by running `python main.py`"
    )


def _print_schema(schema, verbose: int = 0):
    from rich.console import Console
    from rich.table import Table

    table = Table(title="")

    # Add columns
    table.add_column("Input", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Required", style="yellow")
    table.add_column("Default", style="blue")
    table.add_column("Range", style="magenta")

    # Get required fields
    required = schema.get("required", [])

    # Add rows
    for field, info in schema["properties"].items():
        range_str = ""
        if "minimum" in info or "maximum" in info:
            min_val = info.get("minimum", "")
            max_val = info.get("maximum", "")
            range_str = f"{min_val} to {max_val}"

        table.add_row(
            field,
            info.get("format", "") or info.get("type", ""),
            "✓" if field in required else "",
            str(info.get("default", "")),
            range_str,
        )

    Console().print(table)


@functools.lru_cache
def _get_cache_workspace(cpack: str):
    sha = get_sha256(cpack)
    return WORKSPACE_DIR / sha[0:8]


@main.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
    help="Run a ComfyUI package with the given inputs",
    add_help_option=False,
)
@click.argument("cpack", type=click.Path(exists=True, dir_okay=False))
@click.option("--output-dir", "-o", type=click.Path(), default=".")
@click.option("--help", "-h", is_flag=True, help="Show this message and input schema")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity level (use multiple times for more verbosity)",
)
@click.pass_context
def run(ctx, cpack: str, output_dir: str, help: bool, verbose: int):
    from pydantic import ValidationError
    from rich.console import Console

    from .utils import generate_input_model

    inputs = dict(
        zip([k.lstrip("-").replace("-", "_") for k in ctx.args[::2]], ctx.args[1::2])
    )

    console = Console()

    with tempfile.TemporaryDirectory() as temp_dir:
        pack_dir = Path(temp_dir) / ".cpack"
        shutil.unpack_archive(cpack, pack_dir)
        workflow = json.loads((pack_dir / "workflow_api.json").read_text())

    input_model = generate_input_model(workflow)

    # If help is requested, show command help and input schema
    if help:
        console.print(
            'Usage: comfy-pack run [OPTIONS] CPACK --input1 "value1" --input2 "value2" ...'
        )
        console.print("Run a ComfyUI package with the given inputs:")
        _print_schema(input_model.model_json_schema(), verbose)
        return 0

    try:
        validated_data = input_model(**inputs)
        console.print("[green]✓ Input is valid![/green]")
        for field, value in validated_data.model_dump().items():
            console.print(f"{field}: {value}")
    except ValidationError as e:
        console.print("[red]✗ Validation failed![/red]")
        for error in e.errors():
            console.print(f"- {error['loc'][0]}: {error['msg']}")

        console.print("\n[yellow]Expected inputs:[/yellow]")
        _print_schema(input_model.model_json_schema(), verbose)
        return 1

    from .package import install

    workspace = _get_cache_workspace(cpack)
    if not (workspace / "DONE").exists():
        console.print("\n[green]✓ Restoring ComfyUI Workspace...[/green]")
        if workspace.exists():
            shutil.rmtree(workspace)
        install(cpack, workspace, verbose=verbose)
        with open(workspace / "DONE", "w") as f:
            f.write("DONE")
    console.print("\n[green]✓ ComfyUI Workspace is restored![/green]")
    console.print(f"{workspace}")

    from .run import ComfyUIServer, run_workflow

    with ComfyUIServer(str(workspace.absolute()), verbose=verbose) as server:
        console.print("\n[green]✓ ComfyUI is launched in the background![/green]")
        results = run_workflow(
            server.host,
            server.port,
            workflow,
            Path(output_dir).absolute(),
            verbose=verbose,
            workspace=server.workspace,
            **validated_data.model_dump(),
        )
        console.print("\n[green]✓ Workflow is executed successfully![/green]")
        if results:
            console.print("\n[green]✓ Retrieved outputs:[/green]")
        if isinstance(results, dict):
            for field, value in results.items():
                console.print(f"{field}: {value}")
        elif isinstance(results, list):
            for i, value in enumerate(results):
                console.print(f"{i}: {value}")
        else:
            console.print(results)


@main.command(name="build-bento")
@click.argument("source")
@click.option("--name", help="Name of the bento service")
@click.option("--version", help="Version of the bento service")
def bento_cmd(source: str, name: str | None, version: str | None):
    """Build a bento from the source, which can be either a .cpack.zip file or a bento tag."""
    import bentoml
    from bentoml.bentos import BentoBuildConfig

    from .package import build_bento

    with tempfile.TemporaryDirectory() as temp_dir:
        if source.endswith(".cpack.zip"):
            name = name or os.path.basename(source).replace(".cpack.zip", "")
            shutil.unpack_archive(source, temp_dir)
            system_packages = None
            include_default_system_packages = True
        else:
            existing_bento = bentoml.get(source)
            name = name or existing_bento.tag.name
            shutil.copytree(existing_bento.path_of("src"), temp_dir, dirs_exist_ok=True)
            build_config = BentoBuildConfig.from_bento_dir(
                existing_bento.path_of("src")
            )
            requirements_txt = Path(temp_dir) / "requirements.txt"
            if (
                requirements_txt.exists()
                and "comfy-pack" not in requirements_txt.read_text()
            ):
                with open(requirements_txt, "a") as f:
                    f.write("\ncomfy-pack")
            system_packages = build_config.docker.system_packages
            include_default_system_packages = False

        build_bento(
            name,
            Path(temp_dir),
            version=version,
            system_packages=system_packages,
            include_default_system_packages=include_default_system_packages,
        )


def setup_cloud_client(
    ctx: click.Context, param: click.Parameter, value: str | None
) -> str | None:
    from bentoml._internal.configuration.containers import BentoMLContainer

    if value:
        BentoMLContainer.cloud_context.set(value)
        os.environ["BENTOML_CLOUD_CONTEXT"] = value
    return value


@main.command()
@click.argument("bento")
@click.option(
    "-w",
    "--workspace",
    type=click.Path(file_okay=False),
    default="workspace",
    help="Workspace directory, defaults to './workspace'.",
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity level")
@click.option(
    "--context",
    help="BentoCloud context name.",
    expose_value=False,
    callback=setup_cloud_client,
)
def unpack_bento(bento: str, workspace: str, verbose: int):
    """Restore the ComfyUI workspace from a given bento."""
    import bentoml

    from .package import install_comfyui, install_custom_modules, install_dependencies

    bento_obj = bentoml.get(bento)
    comfy_workspace = Path(workspace)
    comfy_workspace.parent.mkdir(parents=True, exist_ok=True)
    if not comfy_workspace.joinpath(".DONE").exists():
        for model in bento_obj.info.models:
            model.to_model().resolve()
        snapshot = json.loads(Path(bento_obj.path_of("src/snapshot.json")).read_text())
        install_comfyui(snapshot, comfy_workspace, verbose=verbose)
        reqs_txt = bento_obj.path_of("env/python/requirements.txt")
        if sys.platform != "linux":
            src_reqs_txt = bento_obj.path_of("src/requirements.txt")
            if os.path.exists(src_reqs_txt):
                click.echo("Using requirements.txt from src directory")
                reqs_txt = src_reqs_txt
        install_dependencies(snapshot, reqs_txt, comfy_workspace, verbose=verbose)

        for f in Path(bento_obj.path_of("src/input")).glob("*"):
            if f.is_file():
                shutil.copy(f, comfy_workspace / "input" / f.name)
            elif f.is_dir():
                shutil.copytree(
                    f, comfy_workspace / "input" / f.name, dirs_exist_ok=True
                )
        install_custom_modules(snapshot, comfy_workspace, verbose=verbose)
        for model in snapshot["models"]:
            if model.get("disabled", False):
                continue
            model_path = comfy_workspace / cast(str, model["filename"])
            if model_path.exists():
                continue
            if model_tag := model.get("model_tag"):
                model_path.parent.mkdir(parents=True, exist_ok=True)
                bento_model = bentoml.models.get(model_tag)
                model_file = bento_model.path_of("model.bin")
                click.echo(f"Copying {model_file} to {model_path}")
                model_path.symlink_to(model_file)
            else:
                click.echo("WARN: Unrecognized model source, the model may be missing")
        comfy_workspace.joinpath(".DONE").touch()

    if os.name == "nt":
        exe = "Scripts/python.exe"
    else:
        exe = "bin/python"
    click.echo(
        f"Workspace is ready at {comfy_workspace}\n"
        f"You can start ComfyUI by running `cd {comfy_workspace} && .venv/{exe} main.py`",
        color="green",
    )
