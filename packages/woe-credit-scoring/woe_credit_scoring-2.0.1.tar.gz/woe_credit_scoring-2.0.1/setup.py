from setuptools import setup, find_packages

setup(
    name="woe-credit-scoring",
    version="2.0.1",
    author="José G. Fuentes, PhD",
    author_email="jose.gustavo.fuentes@comunidad.unam.mx",
    description="Tools for creating credit scoring models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JGFuentesC/woe_credit_scoring/",  # Cambia por tu repositorio
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "seaborn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
