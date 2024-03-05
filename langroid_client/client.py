import requests
from typing import Dict, Any, List, Tuple
import json

class LangroidClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def test(self, x: int) -> int:
        response = requests.post(f"{self.base_url}/test", json={"x": x})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to process text")

    def intellilang_extract_reqs(
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
        response = requests.post(
            f"{self.base_url}/intellilang/extract",
            files=files,
            data=data,
        )

        if response.status_code == 200:
            return response.content
        else:
            raise Exception("Failed to process file")


    def intellilang_eval(
        self,
        reqs_path: str,
        candidate_paths: List[str],
        params: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        files = [('reqs', open(reqs_path, 'rb'))]
        for i, c in enumerate(candidate_paths):
            files.append(('candidates', (c, open(c, 'rb'))))
        response = requests.post(
            f"{self.base_url}/intellilang/eval",
            files=files,
            data={'params': json.dumps(params)},
        )
        if response.status_code == 200:
            # dump to a temp file
            scores_evals_jsonl = "/tmp/scores_evals.jsonl"
            with open(scores_evals_jsonl, "wb") as output_file:
                output_file.write(response.content)

            # recover these as dict objects
            scores = []
            evals = []
            with open(scores_evals_jsonl, "r") as jsonl_file:
                for line in jsonl_file:
                    if "SCORE" in line:
                        scores.append(json.loads(line.replace("SCORE ", "")))
                    else:
                        evals.append(json.loads(line.replace("EVAL ", "")))
            return scores, evals

        else:
            raise Exception("Failed to process file")
