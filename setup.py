from setuptools import setup, find_packages

setup(
    name='aetherpin-connector',
    version='0.1.0',
    description='Link your telescope to the AetherPin live sky map',
    author='AetherPin',
    url='https://github.com/aetherpin/connector',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'astropy>=5.0',
        'watchdog>=3.0',
        'requests>=2.28',
    ],
    entry_points={
        'console_scripts': [
            'aetherpin-connector=agent.cli:main',
        ],
    },
)
