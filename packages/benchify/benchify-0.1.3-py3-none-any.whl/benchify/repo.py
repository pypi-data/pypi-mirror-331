import os
import re
from git import Repo, InvalidGitRepositoryError
from .constants import CONFIG_DIR_PATH

def get_repo(path="."):
    """Get a Git repository object for the given path."""
    try:
        repo = Repo(path, search_parent_directories=True)
        if repo.bare:
            raise ValueError("The repository is bare.")
        return repo
    except InvalidGitRepositoryError:
        raise ValueError(f"No Git repository found at {path}.")


def get_repo_name_and_owner():
    repo = get_repo()
    # Get the remote URL
    remote_url = repo.remotes.origin.url
    # Define patterns for HTTPS and SSH formats
    https_pattern = r'^https://[^/]+/([^/]+)/([^/]+)\.git$'
    ssh_pattern = r'^git@[^:]+:([^/]+)/([^/]+)\.git$'

    # Check for HTTPS URL
    https_match = re.match(https_pattern, remote_url)
    if https_match:
        owner, repo_name = https_match.groups()
        return owner, repo_name

    # Check for SSH URL
    ssh_match = re.match(ssh_pattern, remote_url)
    if ssh_match:
        owner, repo_name = ssh_match.groups()
        return owner, repo_name
    
    print("We were unable to retrieve repository data.")
    exit(1)


def is_benchify_initialized():
    # check if there is .benchify directory
    if os.path.exists(CONFIG_DIR_PATH):
        return True
    return False
