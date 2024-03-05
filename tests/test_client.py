import pytest
from langroid_client import LangroidClient
import requests_mock
import json
from pydantic import BaseModel

class ExtractReqParams (BaseModel):
    num: int

class TestLangroidClient:
    @pytest.fixture
    def client(self):
        return LangroidClient("http://mockapi.com")

    def test_endpoint(self, client):
        # Mock the /test endpoint
        with requests_mock.Mocker() as mocker:
            expected_result = 25
            mocker.post("http://mockapi.com/test", json=expected_result)

            # Call the function
            result = client.test(5)

            # Assert the expected outcome
            assert result == expected_result, "Expected result not returned from /test"

    @pytest.mark.parametrize(
        "reqs_file, cand_file, num",
        [
            ("tests/data/rfp.pdf", "tests/data/candidate.pdf", 2)
        ]
    )
    def test_extract_reqs_endpoint(self, client, reqs_file, cand_file, num):
        # Mock the /extract endpoint
        with requests_mock.Mocker() as mocker:
            expected_response = b"binary data"
            mocker.post(
                "http://mockapi.com/intellilang/extract",
                content=expected_response
            )

            # No need to open files here, just simulate the request
            # Prepare params as expected by FastAPI
            # FastAPI expects JSON-serialized form data, so we serialize `params`
            params = ExtractReqParams(num=num).json()

            # Call the function
            response_content = client.intellilang_extract_reqs(
                reqs_file, cand_file, params
            )

            # Assert the expected outcome
            assert response_content == expected_response, "Expected response content not returned from /extract"


    @pytest.mark.parametrize(
        "reqs_file, cand_files",
        [
            ("tests/data/questions.jsonl", ["tests/data/candidate.pdf"]*2)
        ]
    )
    def test_eval_from_reqs_endpoint(self, client, reqs_file, cand_files):
        # Mock the /extract endpoint
        with requests_mock.Mocker() as mocker:
            expected_response = (
                [dict(a=1, b=2), dict(a=10, b=3)],
                [dict(c=3, d=4), dict(c=5, d=6)]
            )
            expected_response_json = "\n".join(
                [
                    "SCORE " + json.dumps(x) for x in expected_response[0]
                ] + [
                    "EVAL " + json.dumps(x) for x in expected_response[1]
                ]
            )
            mocker.post(
                "http://mockapi.com/intellilang/eval",
                content=expected_response_json.encode("utf-8")
            )

            # No need to open files here, just simulate the request
            # Prepare params as expected by FastAPI
            # FastAPI expects JSON-serialized form data, so we serialize `params`

            # Call the function
            response_content = client.intellilang_eval(reqs_file, cand_files)

            # Assert the expected outcome
            assert response_content == expected_response, "Expected response content not returned from /extract"
