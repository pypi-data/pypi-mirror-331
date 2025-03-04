import requests
from .config import config
from .dto import Error

class IntelliOpsSDK:
    def __init__(self, api_key, base_url=None):
        self.base_url = base_url
        self.api_key = api_key

    def send_error(self, error: Error):
        if not self.api_key:
            raise ValueError("API key is not configured.")

        try:
            headers = {
                "intelliops-api-key": self.api_key,
                "intelliops-service": "alert-service",
            }

            # Serialize the Error object to a Python dictionary
            error_dict = error.model_dump()

            print(f"{error_dict}")

            base_url = self.base_url or config["intelliops_url"]

            response = requests.post(
                f"{base_url}/webhook/error/{self.api_key}",
                json=error_dict,  # Send the dictionary directly
                headers=headers,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print("Error while sending error to intelliops", e)
            print(e.request)
            print(e.strerror)