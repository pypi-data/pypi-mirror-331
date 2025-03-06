from setuptools import setup, find_packages

setup(
    name="user_utils_vb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiogram",
        "boto3",
    ],
    entry_points={
        "console_scripts": [
            "user_utils=user_utils.authenticate_user:main",
        ],
    },
    author="Vitalii Bozadzhy",
    author_email="VitaliiBozadzhy@icloud.com",
    description="A user authentication utility using aiogram and AWS DynamoDB.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VitaliiBozadzhy88/user_utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
