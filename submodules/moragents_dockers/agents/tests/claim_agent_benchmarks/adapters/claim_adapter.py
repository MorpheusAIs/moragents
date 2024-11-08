import json

import requests


class ClaimAdapter:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def ask_agent(self, payload):
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )
