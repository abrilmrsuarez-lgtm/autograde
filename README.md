A Python CLI tool that accepts a public Git repository URL and evaluates whether the following conditions are met:

The target is a valid Git repository
The main branch exists
The feature branch exists on the remote
file1.txt is present on the main branch


Requirements

Python 3.10+
uv (for dependency and environment management)
git available on your PATH

USAGE
uv run autograde \<repository-url\>
