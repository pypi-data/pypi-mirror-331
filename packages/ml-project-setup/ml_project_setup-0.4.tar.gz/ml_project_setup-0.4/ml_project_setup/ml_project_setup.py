import os
import sys
import yaml
import subprocess


def install_framework(framework):
    """Installs the selected ML framework."""
    if framework == "scikit-learn":
        packages = ["scikit-learn"]
    elif framework == "PyTorch":
        packages = ["torch", "torchvision", "torchaudio"]
    elif framework == "TensorFlow":
        packages = ["tensorflow"]
    else:
        return  # No framework to install

    print(f"\n📦 Installing {framework}... This may take a while.")

    for package in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

    print(f"✅ {framework} installed successfully!\n")


def create_file(file_path, content=""):
    """Helper function to create files with default content."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_ml_project(project_name, framework="scikit-learn"):
    """Creates a standardized Machine Learning project structure."""

    # Define project structure
    folders = [
        f"{project_name}/source",
        f"{project_name}/source/components",
        f"{project_name}/source/constants",
        f"{project_name}/source/entity",
        f"{project_name}/source/pipeline",
        f"{project_name}/source/utility",
        f"{project_name}/source/exception",
        f"{project_name}/source/logger",
        f"{project_name}/data",
        f"{project_name}/models",
        f"{project_name}/notebooks",
    ]

    files = {
        f"{project_name}/.gitignore": "*.pyc\n__pycache__/\nvenv/\n",
        f"{project_name}/README.md": f"# {project_name}\n\nAuto-generated ML project structure.\n",
        f"{project_name}/requirements.txt": f"numpy\npandas\n{framework.lower()}\n",
        f"{project_name}/setup_env.sh": "python -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\n",
        f"{project_name}/setup_env.bat": "python -m venv venv\ncall venv\\Scripts\\activate\npip install -r requirements.txt\n",
        f"{project_name}/Dockerfile": """FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
""",
        f"{project_name}/main.py": "from source.pipeline import *\n",
        f"{project_name}/source/logger/logger.py": """import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.info("Logger is set up and ready to use!")
""",
        f"{project_name}/config.yaml": yaml.dump({
            "dataset": {"path": "data/", "train_split": 0.8, "test_split": 0.2},
            "model": {"framework": framework, "learning_rate": 0.001, "batch_size": 32}
        }),
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

    # Install the selected ML framework
    install_framework(framework)


# ✅ **Interactive CLI for Running from Terminal**
def create_project_command():
    """Command-line function to create a new ML project interactively."""

    print("\n🚀 Welcome to ML Project Setup! 🚀")
    project_name = input("Enter your project name: ").strip()

    if not project_name:
        print("❌ Error: Project name cannot be empty.")
        sys.exit(1)

    print("\nSelect ML Framework:")
    print("[1] scikit-learn (default)")
    print("[2] PyTorch")
    print("[3] TensorFlow")
    choice = input("Enter your choice (1/2/3): ").strip()

    framework_map = {"1": "scikit-learn", "2": "PyTorch", "3": "TensorFlow"}
    framework = framework_map.get(choice, "scikit-learn")

    create_ml_project(project_name, framework)
    print(f"\n✅ Project '{project_name}' created with {framework} framework!")


if __name__ == "__main__":
    create_project_command()
