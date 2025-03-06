import requests

class MedDataSDK:
    def __init__(self, api_key, api_endpoint="http://127.0.0.1:3000/api/getData"):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def fetch_all_conversations(self):
        try:
            response = requests.get(f"{self.api_endpoint}?apiKey={self.api_key}")

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.reason}")

            return response.json()
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return None
