from abc import ABC, abstractmethod
from typing import List
from git import Repo


class FileContent:
    def __init__(self, file_path: str, content: str):
        self.file_path: str = file_path
        self.content: str  = content


class FilePatch:
    def __init__(self, file_path: str, patch: str):
        self.file_path: str = file_path
        self.patch: str = patch


class PullRequest:
    def __init__(self,
                 pull_request_number: int,
                 title: str,
                 description: str,
                 head_sha: str,
                 changes: List[FilePatch]=None):
        self.id: int = pull_request_number
        self.title: str = title
        self.description: str = description
        self.head_sha: str = head_sha
        self.changes: List[FilePatch] = changes


class GitRepository(ABC):
    @abstractmethod
    def get_pull_requests(self) -> List[PullRequest]:
        pass

    @abstractmethod
    def get_pull_request_changes(self, pull_request: PullRequest) -> List[FilePatch]:
        pass

    @abstractmethod
    def clone(self, path: str) -> Repo:
        pass

    @staticmethod
    def _clone_repository(repository_url: str, path: str, no_checkout=True) -> Repo:
        repo = Repo.clone_from(url=repository_url, to_path=path, no_checkout=no_checkout)
        return repo
