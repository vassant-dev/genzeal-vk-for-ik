from typing import List, Tuple
from urllib.parse import urlparse
from ghapi.all import GhApi, paged
from git import Repo

from ..core import GitRepository, FileContent, PullRequest, FilePatch


class GitHubRepository(GitRepository):
    def __init__(self,repository_url: str,token: str=None):
        self.token: str = token
        self.owner, self.repo = GitHubRepository._parse_repository_url(repository_url)
        self.local_repo = None
        self.api = GhApi(
            owner=self.owner,
            repo=self.repo,
            token=self.token
        )

    def get_pull_requests(self) -> List[PullRequest]:
        pull_requests = []
        pages = paged(self.api.pulls.list)
        for page in pages:
            for item in page:
                pr = PullRequest(
                    pull_request_number=item.number,
                    title=item.title,
                    description=item.body,
                    head_sha=item.head.sha,
                )
                pull_requests.append(pr)
        return pull_requests

    def get_pull_request_changes(self, pull_request: PullRequest) -> List[FilePatch]:
        patches = []
        pages = paged(self.api.pulls.list_files, pull_number=pull_request.id)
        for page in pages:
            for item in page:
                patch = FilePatch(file_path=item.filename, patch=item.patch)
                patches.append(patch)
        return patches

    def clone(self, path: str):
        self.local_repo = self._clone_repository(self._create_repo_url(), path)

    def get_pull_request_head_content(self) -> List[FileContent]:
        pass
        # if self.local_repo is None:
        #     raise ValueError("Repository is not cloned locally. Please clone it first.")
        

    def _create_repo_url(self):
        prefix = ""
        if self.token is not None and len(self.token.strip()) > 0:
            prefix = f"{self.token}@"
        return f"https://{prefix}github.com/{self.owner}/{self.repo}"

    @staticmethod
    def _parse_repository_url(url: str) -> Tuple[str,str]:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 2:
            owner: str = path_parts[0]
            repo: str = path_parts[1]
            return owner, repo
        else:
            raise ValueError("Invalid github repository url. It must be in format https://github.com/<owner>/<repository name>")
