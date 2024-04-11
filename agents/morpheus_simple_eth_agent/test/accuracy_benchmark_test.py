import json
import unittest

from chains_and_agents.morpheus_chain import process_nlq
from chains_and_agents.utils.extract_json import extract_json_payload_and_clean

from test.assets.simple_questions import qa_pairs


def is_subset(dict1, dict2):
    """Check if dict1 is a subset of dict2, including nested dictionaries."""
    for key, value in dict1.items():
        if key not in dict2:
            return False
        if isinstance(value, dict):
            # If the value is a dictionary, recurse.
            if not isinstance(dict2[key], dict) or not is_subset(value, dict2[key]):
                return False
        elif isinstance(value, list):
            # If the value is a list, ensure all elements are in the corresponding list in dict2.
            # This assumes you want to check for the presence of the values, not their order or frequency.
            if not isinstance(dict2[key], list) or any(item not in dict2[key] for item in value):
                return False
        else:
            if value != dict2[key]:
                return False
    return True


nlq_id2accuracy = {
    d["qa_id"]: []  # will contain pass/fail info
    for d in qa_pairs
}

for qa_pair in qa_pairs:
    qa_id = qa_pair["qa_id"]
    target_payload = qa_pair["payload"]

    for nlq in qa_pair["nlq"]:
        response = process_nlq(nlq)

        try:
            response_object = json.loads(extract_json_payload_and_clean(response)[0])
            del response_object['id']  # we don't care about the nonce

            passed = is_subset(target_payload, response_object)

            if passed:
                nlq_id2accuracy[qa_id].append(True)
            else:
                nlq_id2accuracy[qa_id].append(False)

        except BaseException as e:
            nlq_id2accuracy[qa_id].append(False)


for key in nlq_id2accuracy:
    true_count = sum(nlq_id2accuracy[key])
    total_count = len(nlq_id2accuracy[key])
    percentage = (true_count / total_count) * 100
    print(f"The percentage of True values in {key} is {percentage:.2f}%")
