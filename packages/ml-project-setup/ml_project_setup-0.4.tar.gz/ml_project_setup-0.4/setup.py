from setuptools import setup, find_packages

setup(
    name="ml-project-setup",
    version="0.4",
    author="Amogh Pathak",
    author_email="amogh9792@gmail.com",
    description="A package to auto-generate structured ML project folders",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "scikit-learn", "pyyaml"],
    entry_points={
        "console_scripts": [
            "mlsetup = ml_project_setup.ml_project_setup:create_project_command"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
