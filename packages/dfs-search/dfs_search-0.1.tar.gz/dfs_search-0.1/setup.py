from setuptools import setup, find_packages

setup(
    name="dfs_search",  # Package name
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
    author="M. Umer Aziz",  # Replace with your name
    author_email="u.aziz7560@gmail.com",  # Replace with your email
    description="A simple DFS-based search library",
    url="https://github.com/umercodes27/dfs_search",  # Replace with your GitHub repo

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
