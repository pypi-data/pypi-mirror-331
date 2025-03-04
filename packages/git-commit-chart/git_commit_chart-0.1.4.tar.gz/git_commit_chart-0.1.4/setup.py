from setuptools import setup, find_packages

setup(
    name="git-commit-chart",
    version="0.1.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=3.0.2",
        "requests>=2.31.0",
        "python-dotenv>=1.0.1",
        "waitress>=2.1.2",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "pytest-timeout>=2.2.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "git-commit-chart=git_commit_chart.app:main",
        ],
    },
    author="Jesse Goodier",
    description="A web application to visualize GitHub repository commit history, written by cursor AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="github, commits, visualization, chart",
    url="https://github.com/jessegoodier/git-commit-chart",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
) 