from abc import ABC, abstractmethod
from . import PullRequest


def get_pull_request_prompt_content(pull_request: PullRequest) -> str:
    header_content = f"Pull request title: {pull_request.title}"
    if pull_request.changes is not None:
        change_content = "\n\n\n".join([f"File: {change.file_path}\n{change.patch}" for change in pull_request.changes])
    else:
        change_content = "No changes available"
    pr_content = f"{header_content}\n\nPull request changes:\n{change_content}"
    return pr_content


class PullRequestReviewer(ABC):
    @abstractmethod
    def review(self, pull_request: PullRequest) -> str:
        pass
