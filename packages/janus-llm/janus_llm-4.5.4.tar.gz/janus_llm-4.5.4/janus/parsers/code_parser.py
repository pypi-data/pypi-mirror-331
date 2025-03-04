import re

from langchain_core.messages import BaseMessage

from janus.parsers.parser import JanusParser, JanusParserException
from janus.utils.logger import create_logger

log = create_logger(__name__)


class CodeParser(JanusParser):
    language: str

    def parse(self, text: str | BaseMessage) -> str:
        if isinstance(text, BaseMessage):
            text = str(text.content)
        pattern = rf"```[^\S\r\n]*(?:{self.language}[^\S\r\n]*)?\n?(.*?)\n*```"
        code = re.search(pattern, text, re.DOTALL)
        if code is None:
            raise JanusParserException(
                text,
                "Code not find code between triple backticks",
            )
        return str(code.group(1))

    def get_format_instructions(self) -> str:
        return "Output must contain text contained within triple backticks (```)"
