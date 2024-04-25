import re


def clean_json_string(s):
    """
    Attempt to clean a JSON string by removing comments and fixing common issues
    like trailing commas that can result in invalid JSON.
    """
    # Remove comments
    s = re.sub(r'//.*?\n', '\n', s)

    # Attempt to fix trailing commas within objects or arrays
    s = re.sub(r',\s*([\]}])', r'\1', s)

    return s


def extract_json_payload_and_clean(text):
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, text, re.DOTALL)
    cleaned_matches = []
    for match in matches:
        cleaned_match = clean_json_string(match)
        # Minify JSON by removing newlines and excessive spaces
        cleaned_match = re.sub(r'\s+', ' ', cleaned_match).strip()
        cleaned_matches.append(cleaned_match)
    return cleaned_matches

