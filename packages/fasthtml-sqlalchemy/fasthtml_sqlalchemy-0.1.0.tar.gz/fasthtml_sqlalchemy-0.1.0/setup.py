from setuptools import setup, find_packages

setup(
    name="fasthtml-sqlalchemy",
    version="0.1.0",
    description="SQLAlchemy integration for FastHTML",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="José María Sánchez González",
    author_email="jmsanchez.ibiza@gmail.com",
    url="https://github.com/jmsanchez-ibiza/fasthtml-sqlalchemy",
    packages=find_packages(),
    install_requires=[
        "python-fasthtml",
        "sqlalchemy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)