import re


def is_confluence_url(url):
    pattern = r'https://[a-zA-Z0-9.-]+\.atlassian\.net/wiki/spaces/[a-zA-Z0-9]+/(pages/[0-9]+/[a-zA-Z0-9+]+|overview)'
    return bool(re.match(pattern, url))
