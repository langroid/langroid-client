import requests
from typing import Dict, Any
import json

class LangroidClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def dummy(self, x: int) -> int:
        response = requests.post(f"{self.base_url}/test", json={"x": x})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to process text")

    def extract_reqs(
        self,
        reqs_path: str,
        candidate_path: str,
        params: Dict[str, Any]
    ) -> bytes:
        files = {
            'reqs': open(reqs_path, 'rb'),
            'candidate': open(candidate_path, 'rb'),
        }
        data = {'params': json.dumps(params)}
        response = requests.post(f"{self.base_url}/extract", files=files, data=data)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception("Failed to process file")


    def eval_from_reqs(
        self,
        reqs_path: str,
        candidate_path: str,
    ) -> bytes:
        files = {
            'reqs': open(reqs_path, 'rb'),
            'candidate': open(candidate_path, 'rb'),
        }
        response = requests.post(f"{self.base_url}/eval", files=files)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception("Failed to process file")
