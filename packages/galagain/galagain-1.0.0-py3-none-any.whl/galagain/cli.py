import sys
import argparse
from pathlib import Path


def create_project(
    project_name,
    project_path=None,
    python_version="3.10.0",
    author_name="galagain",
    author_email="calvin@galagain.com",
):
    if project_path:
        project_dir = Path(project_path).resolve() / project_name
    else:
        project_dir = Path(project_name).resolve()

    print(f"Creating project {project_name} at {project_dir}")

    src_dir = project_dir / "src" / project_name
    test_dir = project_dir / "tests"

    for folder in [src_dir, test_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").touch()
    (project_dir / "README.md").write_text(f"# {project_name}\n")
    (project_dir / ".gitignore").write_text("__pycache__/\n.gitignore\n")

    conda_env_file = project_dir / "environment.yml"
    conda_env_file.write_text(
        f"name: {project_name}_env\n"
        f"channels:\n"
        " - conda-forge\n"
        " - nodefaults\n"
        "dependencies:\n"
        f" - conda-forge::python={python_version}\n"
        " - conda-forge::pip\n"
        " - conda-forge::poetry\n"
    )

    poetry_toml = project_dir / "pyproject.toml"
    poetry_toml.write_text(
        f"[tool.poetry]\n"
        f'name = "{project_name}"\n'
        f'version = "0.1.0"\n'
        f'description = ""\n'
        f'authors = ["{author_name} <{author_email}>"]\n\n'
        "[tool.poetry.dependencies]\n"
        f'python = "{python_version}"\n\n'
        "[build-system]\n"
        'requires = ["poetry-core"]\n'
        'build-backend = "poetry.core.masonry.api"\n'
    )

    print(f"{project_name} created successfully!\n")
    print("_" * 10)
    print(f"cd {project_dir}")
    print("conda env create -f environment.yml")
    print(f"conda activate {project_name}_env")
    print("poetry install")
    print("git init")
    print("git add .")
    print("git commit -m 'Initial commit'")
    print("_" * 10)


def main():
    parser = argparse.ArgumentParser(
        description="Create a Python project with Conda and Poetry."
    )
    parser.add_argument("create", help="Command to create a project.")
    parser.add_argument("project_name", help="Project name.")
    parser.add_argument("--path", help="Project path (optional).", default=None)
    parser.add_argument(
        "--python", help="Python version (default: 3.10.0).", default="3.10.0"
    )
    parser.add_argument(
        "--name", help="Author's name (default: galagain).", default="galagain"
    )
    parser.add_argument(
        "--email",
        help="Author's email (default: calvin@galagain.com).",
        default="calvin@galagain.com",
    )

    args = parser.parse_args()

    if args.create != "create":
        parser.print_help()
        sys.exit(1)

    create_project(
        project_name=args.project_name,
        project_path=args.path,
        python_version=args.python,
        author_name=args.name,
        author_email=args.email,
    )


if __name__ == "__main__":
    main()
