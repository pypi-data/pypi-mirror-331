from setuptools import setup, find_packages

version = '1.0.1'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="certbot-dns-beget-api",
    version=version,
    description="Beget DNS plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Medan-rfz",
    license="MIT License",
    url="https://github.com/Medan-rfz/certbot-dns-beget-api",
    packages=find_packages(),
    install_requires=[
        "certbot",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-beget-api = certbot_dns_beget.dns_beget_api:Authenticator",
        ],
    },
)
