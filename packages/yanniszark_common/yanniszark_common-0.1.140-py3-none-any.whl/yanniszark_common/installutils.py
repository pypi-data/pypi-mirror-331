#!/usr/bin/env python3

import logging
import argparse

from abc import ABC, abstractmethod
from yanniszark_common.gitutils import validate_repo, clone_or_adopt


log = logging.getLogger(__name__)


class RepoInstallerCLI(ABC):
    def __init__(self, name: str, default_repo_url: str,
                 default_repo_path: str, default_version: str):
        self.name = name
        self.default_repo_url = default_repo_url
        self.default_repo_path = default_repo_path
        self.default_version = default_version

    def parse_args(self):
        parser = argparse.ArgumentParser("Build and install %s" % self.name)
        parser.add_argument("--repo-path",
                            default=self.default_repo_path,
                            help="Where to place %s repo." % self.name)
        parser.add_argument("--repo-url",
                            default=self.default_repo_url,
                            help="%s repo URL." % self.name)
        parser.add_argument("--version", default=self.default_version,
                            help="Version to install.")
        return parser.parse_args()

    def install(self):
        logging.basicConfig(level=logging.INFO)
        args = self.parse_args()
        repo_url = args.repo_url
        repo_path = args.repo_path
        repo_version = args.version
        repo = clone_or_adopt(repo_url, repo_path)
        validate_repo(repo)
        repo.git.checkout(repo_version)
        log.info("Installing RocksDB build dependencies")
        self.do_install_deps(repo_path)
        log.info("Building and installing RocksDB '%s'" % repo_version)
        self.do_build(repo_path)
        self.do_install(repo_path)

    @abstractmethod
    def do_install_deps(self):
        raise NotImplementedError

    @abstractmethod
    def do_build(self):
        raise NotImplementedError

    @abstractmethod
    def do_install(self):
        raise NotImplementedError
