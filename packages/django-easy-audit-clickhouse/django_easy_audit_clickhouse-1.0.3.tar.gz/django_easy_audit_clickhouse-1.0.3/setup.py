import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-easy-audit-clickhouse",
    version="1.0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.2",
        "djangorestframework>=3.15",
        "celery>=5.4.0",
        "clickhouse-connect>=0.8.15",
    ],
    python_requires=">=3.5",
    license_files=["LICENSE.txt"],
    description="Django Easy Audit Log with ClickHouse integration",
    long_description=README,
    url="https://github.com/houseworksinc/django-easy-audit-clickhouse",
    classifiers=[
        "Environment :: Plugins",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
