import requests
import json

url = 'http://127.0.0.1:5000/'

headers = {
    'Content-Type': 'application/json',
}

def ask_agent(payload):
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Raw response data:")
        print(response.text)
        return response.json()
    else:
        print("Raw error data:")
        print(response.text)
        raise Exception(f"Request failed with status code {response.status_code}")

# Step 1: Request to claim MOR rewards
payload = {
    "prompt": {"role": "user", "content": "I want to claim my MOR rewards from pool id 1"},
    "wallet_address": "0x48d0EAc727A7e478f792F16527012452a000f2bd"
}
response = ask_agent(payload)

# Step 2: Provide the receiver address
receiver_address = "0x48d0EAc727A7e478f792F16527012452a000f2bd"
payload = {
    "prompt": {"role": "user", "content": receiver_address},
    "wallet_address": "0x48d0EAc727A7e478f792F16527012452a000f2bd"
}
response = ask_agent(payload)

# Step 3: Confirm the transaction
payload = {
    "prompt": {"role": "user", "content": "proceed"},
    "wallet_address": "0x48d0EAc727A7e478f792F16527012452a000f2bd"
}
response = ask_agent(payload)

# Final step: Print the final raw response after confirming
print("Final raw response data:")
print(json.dumps(response, indent=2))
