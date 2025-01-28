from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from ..core import PullRequestReviewer, get_pull_request_prompt_content, PullRequest
from .prompts import SYSTEM_PROMPT, SIMPLE_REVIEWER_PROMPT


class SimpleReviewer(PullRequestReviewer):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.chain = self._create_review_chain()

    def review(self, pull_request: PullRequest) -> str:
        pr_content: str = get_pull_request_prompt_content(pull_request)
        response: str = self.chain.invoke({"pr_content": pr_content})
        return response

    def _create_review_chain(self):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", SIMPLE_REVIEWER_PROMPT)
        ])
        output_parser = StrOutputParser()
        chain = prompt_template | self.llm | output_parser
        return chain