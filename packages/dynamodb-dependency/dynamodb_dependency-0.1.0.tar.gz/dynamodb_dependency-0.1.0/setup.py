from setuptools import setup, find_packages

setup(
    name="dynamodb_dependency",
    version="0.1.0",
    author="Vitalii Bozadzhy",
    author_email="VitaliiBozadzhy@icloud.com",
    description="dependency for DynamoDB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VitaliiBozadzhy88/dynamodb_dependency",
    packages=find_packages(),
    install_requires=["boto3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
