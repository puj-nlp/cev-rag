import requests
import json

# Define the server endpoint and model details
URL = "http://127.0.0.1:27685/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json"
    # "Authorization": "Bearer <YOUR_API_KEY>" # If your local API requires a token
}

# Define the question you want to ask
question = "What are the impacts of deforestation in Colombia?"

# Define the payload according to your API's expected format
payload = {
    "model": "meta-llama/Llama-3.1-70B-Instruct",
    "messages": [
        {"role": "user", "content": question}
    ],
    "temperature": 0.7
}

# Make the POST request to your LLM endpoint
try:
    response = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()  # This will raise an error for bad status codes
    data = response.json()
    print(json.dumps(data, indent=2))  # Print the response in a readable format
except requests.exceptions.RequestException as e:
    print(f"Failed to connect to the model: {e}")
