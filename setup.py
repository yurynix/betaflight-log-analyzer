from setuptools import setup, find_packages

setup(
    name="betaflight-log-analyzer",
    version="0.1.0",
    description="Tool for analyzing Betaflight blackbox logs and providing PID tuning recommendations",
    author="Yury M",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
    ],
    entry_points={
        'console_scripts': [
            'betaflight-log-analyzer=betaflight_log_analyzer.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 