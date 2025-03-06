import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "mbonig.secret",
    "version": "0.0.5",
    "description": "An AWS CDK construct for creating a secret in AWS Secrets Manager, without losing manually changed values.",
    "license": "MIT",
    "url": "https://github.com/mbonig/secret.git",
    "long_description_content_type": "text/markdown",
    "author": "Matthew Bonig<matthew.bonig@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/mbonig/secret.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "mbonig_secret",
        "mbonig_secret._jsii"
    ],
    "package_data": {
        "mbonig_secret._jsii": [
            "secret@0.0.5.jsii.tgz"
        ],
        "mbonig_secret": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.181.1, <3.0.0",
        "constructs>=10.1.203, <11.0.0",
        "jsii>=1.108.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
