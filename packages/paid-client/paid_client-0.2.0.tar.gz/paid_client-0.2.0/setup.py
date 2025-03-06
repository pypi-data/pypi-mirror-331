from setuptools import setup, find_packages

setup(
    name="paid_client",
    version="0.2.0",
    author="Paid.ai",
    author_email="raj@agentpaid.ai",
    description="A package to handle transaction events and send payloads.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgentPaid/ap-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
