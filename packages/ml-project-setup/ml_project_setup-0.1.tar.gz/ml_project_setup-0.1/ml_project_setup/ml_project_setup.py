import os
import sys


def create_file(file_path, content=""):
    """Helper function to create files with default content."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_ml_project(project_name):
    """Creates a standardized Machine Learning project structure."""

    folders = [
        f"{project_name}/source",
        f"{project_name}/source/components",
        f"{project_name}/source/constants",
        f"{project_name}/source/entity",
        f"{project_name}/source/pipeline",
        f"{project_name}/source/utility",
        f"{project_name}/source/exception",
        f"{project_name}/source/logger",
    ]

    files = {
        f"{project_name}/.gitignore": "*.pyc\n__pycache__/\n",
        f"{project_name}/README.md": "# Machine Learning Project\n",
        f"{project_name}/requirements.txt": "numpy\npandas\nscikit-learn\n",
        f"{project_name}/main.py": "from source.pipeline import *\n",
        f"{project_name}/setup.py": '''from setuptools import setup, find_packages

setup(
    name="''' + project_name + '''",
    version="0.1",
    packages=find_packages(where="source"),
    package_dir={"": "source"},
    install_requires=["numpy", "pandas", "scikit-learn"],
)
''',
    }

    # Create directories
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create __init__.py for packages
    for folder in folders:
        create_file(f"{folder}/__init__.py")

    # Create required files
    for file_path, content in files.items():
        create_file(file_path, content)

    print(f"✅ ML project '{project_name}' created successfully!")


# ✅ **CLI Function for Running from Terminal**
def create_project_command():
    """Command-line function to create a new ML project."""
    if len(sys.argv) < 2:
        print("❌ Error: Please specify a project name.")
        print("Usage: mlsetup <project_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    create_ml_project(project_name)


if __name__ == "__main__":
    create_project_command()
