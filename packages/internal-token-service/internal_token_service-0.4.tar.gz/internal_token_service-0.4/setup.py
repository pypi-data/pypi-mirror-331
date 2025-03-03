from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name='internal_token_service',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'PyJWT>=2.0.0'
    ],
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',  # Add your license type here (e.g., MIT)
    include_package_data=True,
)
