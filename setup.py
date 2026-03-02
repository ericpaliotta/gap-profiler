from setuptools import setup, find_packages
# List of requirements
requirements = []  # This could be retrieved from requirements.txt
# Package (minimal) configuration
setup(
    name="gap_profiler",
    version="1.0.0",
    description="profile visualization for the GAP language",
    packages=find_packages(),  # __init__.py folders search
    install_requires=requirements
)