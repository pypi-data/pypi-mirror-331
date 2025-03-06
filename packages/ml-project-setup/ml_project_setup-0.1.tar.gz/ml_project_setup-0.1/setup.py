from setuptools import setup, find_packages

setup(
    name="ml_project_setup",
    version="0.1",
    author="Amogh Pathak",
    author_email="amogh9792@gmail.com",
    description="A standardized machine learning project structure",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "scikit-learn"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mlsetup = ml_project_setup.ml_project_setup:create_project_command"
        ]
    },
)
