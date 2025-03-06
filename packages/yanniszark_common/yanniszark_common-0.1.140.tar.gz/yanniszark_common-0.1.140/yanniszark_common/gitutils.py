import os
from git.repo import Repo


def validate_repo(repo: Repo):
    """Validate a git repo's condition before using it.

    Current checks:
    - Is the repo dirty?
    - Are there untracked files?

    TODO:
    - Is the repo in the middle of a rebase?
    - Is the repo in the middle of a cherry-pick?
    """
    if repo.is_dirty():
        raise AttributeError("Repo '%s' is dirty" % repo.working_dir)
    if repo.untracked_files:
        raise AttributeError("Repo '%s' has untracked files"
                             % repo.working_dir)
    return


def clone_or_adopt(url: str, path: str) -> Repo:
    if os.path.exists(path) and os.listdir(path):
        repo = Repo(path)
        found = False
        for remote in repo.remotes:
            for r_url in remote.urls:
                if url == r_url:
                    found = True
        if not found:
            raise AttributeError("Repo '%s' already exists but doesn't have"
                                 " '%s' as a remote!"
                                 % (repo.working_dir, url))
    else:
        repo = Repo.clone_from(url, path)
    # validate_repo(repo)
    return repo
