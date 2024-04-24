import os.path

import requests
from typing import Dict, Any, List, Tuple
import json
import mimetypes

class LangroidClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def agent_query(self, text: str, openai_api_key:str) -> str:
        headers = {
            "openai-api-key": openai_api_key,
        }
        response = requests.post(
            f"{self.base_url}/agent/query",
            json={"query": text},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to process query")

    def test(self, x: int) -> int:
        response = requests.post(f"{self.base_url}/test", json={"x": x})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to process text")

    def langroid_askdoc(
        self,
        doc: str,
        query: str,
        openai_api_key: str,
    ) -> str:
        headers = {
            "openai-api-key": openai_api_key,
        }

        doc_mime_type, _ = mimetypes.guess_type(doc)
        route = "langroid/askdoc"
        with open(doc, 'rb') as doc_bytes:
            files = {
                'doc': (os.path.basename(doc), doc_bytes, doc_mime_type),
            }
            response = requests.post(
                f"{self.base_url}/{route}",
                files=files,
                data=dict(query=json.dumps({"query": query})),
                headers=headers,
            )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to process request")

    def _intellilang_extract_reqs_general(
        self,
        reqs_path: str,
        candidate_path: str,
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
        rag: bool,
    ) -> Tuple[bool, bytes|str]:
        req_mime_type, _ = mimetypes.guess_type(reqs_path)
        candidate_mime_type, _ = mimetypes.guess_type(candidate_path)
        # files = {
        #     'reqs': open(reqs_path, 'rb'),
        #     'candidate': open(candidate_path, 'rb'),
        # }
        headers = {
            "openai-api-key": openai_api_key,
            "doc-type": doc_type,
        }
        data = dict(params = json.dumps(params))
        route = "intellilang/extract-rag" if rag else "intellilang/extract"
        with open(reqs_path, 'rb') as reqs, open(candidate_path, 'rb') as candidate:
            files = {
                'reqs': (os.path.basename(reqs_path), reqs, req_mime_type),
                'candidate': (os.path.basename(candidate_path),
                              candidate, candidate_mime_type),
            }
            response = requests.post(
                f"{self.base_url}/{route}",
                files=files,
                data=data,
                headers=headers,
            )

        if response.status_code == 200:
            return (True, response.content)
        else:
            return (
                False,
                response.json().get(
                    "message",
                    "An error occurred but no message was provided"
                )
            )

    def intellilang_extract_reqs(
        self,
        reqs_path: str,
        candidate_path: str,
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
    ) -> Tuple[bool, bytes|str]:
        return self._intellilang_extract_reqs_general(
            reqs_path,
            candidate_path,
            params,
            openai_api_key,
            doc_type,
            rag=False,
        )

    def intellilang_extract_reqs_rag(
        self,
        reqs_path: str,
        candidate_path: str,
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
    ) -> Tuple[bool, bytes|str]:
        return self._intellilang_extract_reqs_general(
            reqs_path,
            candidate_path,
            params,
            openai_api_key,
            doc_type,
            rag=True,
        )

    def _intellilang_eval_general(
        self,
        reqs_path: str,
        candidate_paths: List[str],
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
        rag: bool,
    ) -> Tuple[bool, Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] | str]:
        files = [('reqs', open(reqs_path, 'rb'))]
        for i, c in enumerate(candidate_paths):
            files.append(('candidates', (c, open(c, 'rb'))))
        headers = {
            "openai-api-key": openai_api_key,
            "doc-type": doc_type,
        }
        route = "intellilang/eval-rag" if rag else "intellilang/eval"
        response = requests.post(
            f"{self.base_url}/{route}",
            files=files,
            data={'params': json.dumps(params)},
            headers=headers,
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
                    dct = json.loads(line)
                    if dct["type"] == "SCORE":
                        scores.append(dct)
                    else:
                        evals.append(dct)
            # from each dict in evals, scores, drop the `type` key
            for e in evals:
                e.pop("type")
            for s in scores:
                s.pop("type")
            return (True, (scores, evals))

        else:
            raise (
                False,
                response.json().get("message",
                                    "An error occurred but no message was provided")
            )

    def intellilang_eval(
        self,
        reqs_path: str,
        candidate_paths: List[str],
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
    ) -> Tuple[bool, Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] | str]:
        return self._intellilang_eval_general(
            reqs_path,
            candidate_paths,
            params,
            openai_api_key,
            doc_type,
            rag=False,
        )

    def intellilang_eval_rag(
        self,
        reqs_path: str,
        candidate_paths: List[str],
        params: Dict[str, Any],
        openai_api_key: str,
        doc_type: str,
    ) -> Tuple[bool, Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] | str]:
        return self._intellilang_eval_general(
            reqs_path,
            candidate_paths,
            params,
            openai_api_key,
            doc_type,
            rag=True,
        )