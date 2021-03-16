import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="alertmanager-gchat-integration",
    version="1.0.4",
    description="The application provides a Webhook integration for Prometheus AlertManager to push alerts to Google Chat rooms.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/julb/alertmanager-gchat-integration",
    author="Julb",
    author_email="julien@julb.me",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["alertmanager_gchat_integration"],
    include_package_data=True,
    install_requires=[
        "flask==1.1.2",
        "prometheus-flask-exporter==0.18.1",
        "gunicorn==20.0.4",
        "toml",
        "requests",
        "jinja2",
        "iso8601==0.1.14",
    ],
)
