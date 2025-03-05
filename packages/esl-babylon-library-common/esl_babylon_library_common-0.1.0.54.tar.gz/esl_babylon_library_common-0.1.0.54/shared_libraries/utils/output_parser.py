import json
import re
from typing import List, Any

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.outputs import Generation
from langchain_core.utils.json import parse_json_markdown

from shared_libraries.utils.json_utils import repair_json


class BabylonJsonOutputParser(JsonOutputParser):
    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Any:
        text = result[0].text
        text = text.strip()
        text = text.replace(" None", " null")
        text = self.identify_type_and_parse(text)
        if partial:
            try:
                return parse_json_markdown(text)
            except json.JSONDecodeError:
                return None
        else:
            try:
                return parse_json_markdown(text)
            except json.JSONDecodeError:
                msg = f"Invalid json output: {text}"
                try:
                    fixed_json = self.extract_json(repair_json(text))
                    return json.loads(fixed_json)
                except json.JSONDecodeError as e:
                    raise OutputParserException(msg, llm_output=text) from e

    def identify_type_and_parse(self, json_str) -> str:
        first_bracket = ""
        for i in json_str:
            if i in ["[", "{"]:
                first_bracket = i
                break

        if first_bracket == "[":
            return self.extract_json_list(json_str)
        elif first_bracket == "{":
            return self.extract_json_dict(json_str)
        else:
            return json_str

    @staticmethod
    def extract_json_dict(text: str) -> str:
        match = re.search(r'\{.*\}', text, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(0)
        return text

    @staticmethod
    def extract_json_list(text: str) -> str:
        match = re.search(r'\[.*\]', text, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(0)
        return text
