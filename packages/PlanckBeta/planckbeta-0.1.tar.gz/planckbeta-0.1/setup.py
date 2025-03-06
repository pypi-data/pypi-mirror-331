from setuptools import setup, find_packages

setup(
    name="PlanckBeta",
    version="0.1",
    packages=find_packages(),
    install_requires=["requests"],
    author="Plan Air Studio",
    description="PlanckBeta SDK for interacting with Planck AI models",
    url="https://github.com/yourgithub/PlanckBeta",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
