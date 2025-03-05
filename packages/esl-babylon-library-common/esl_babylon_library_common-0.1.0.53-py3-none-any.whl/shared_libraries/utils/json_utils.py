import json
import re

from shared_libraries.utils.color_print import cprint, Colors


def preprocess_json(json_str: str) -> str:
    corrected_str = re.sub(pattern=r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})',
                           repl=r"\\\\",
                           string=json_str)
    match = re.search(pattern=r"\{.*}",
                      string=corrected_str,
                      flags=re.MULTILINE | re.DOTALL)
    if match:
        return match.group(0)
    return corrected_str


def repair_json(json_str):
    try:
        # Try to parse the given json string
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except Exception as e:
        cprint(f"Failed to parse json: {str(e)}", color=Colors.RED.value)
        cprint(f"Trying to repair: {str(e)}", color=Colors.RED.value)
        return clean_json(json_str)


def clean_json(json_str):
    bracket_dict = {"{": "}", "[": "]"}
    all_brackets = ["[", "]", "{", "}"]
    close_brackets = ["]", "}"]
    brackets = []
    for c in json_str:
        if c not in all_brackets:
            continue

        if c in bracket_dict.keys():
            brackets.append(c)
            continue

        if brackets and bracket_dict[brackets[-1]] == c:
            brackets.pop()

    fill_json = ""
    for br in brackets[::-1]:
        fill_json += bracket_dict[br]

    fixed_json = json_str
    while fixed_json and fixed_json[-1] not in close_brackets:
        fixed_json = fixed_json[:-1]

    if fixed_json:
        fixed_json = fixed_json + ''.join(fill_json)
        return fixed_json
    json_str = json_str + ''.join(fill_json)
    return json_str
