from setuptools import setup, find_packages

setup(
    name="WebStarterKit",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "WebStarterKit=project_creator.cli:main",
        ],
    },
    author="Shubham Parida",
    author_email="paridashub9871@gmail.com",  # Add your email
    description="A CLI tool to generate a basic HTML, CSS, and JS project structure.",
    long_description=open("README.md").read(),  # Ensures long description
    long_description_content_type="text/markdown",  # Specifies markdown format
    url="https://github.com/shubham-parida01/WebStarterKit",  # Add your repo URL if applicable
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Ensures compatibility
)
