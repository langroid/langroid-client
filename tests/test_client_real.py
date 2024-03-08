import pytest
from langroid_client import LangroidClient
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class ExtractReqParams (BaseModel):
    num: int

class EvalParams (BaseModel):
    start_idx: int

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "http://localhost:80"
#BASE_URL = "https://langroid-server-zb43tal5mq-uk.a.run.app"

class TestLangroidClientRealEndpoint:
    @pytest.fixture
    def client(self):
        return LangroidClient(BASE_URL)

    def test_toy_endpoint(self, client):
        result = client.test(5)
        assert result == 25, "Expected result not returned from /test"


    def test_query_endpoint(self, client):
        # Call the function
        result = client.agent_query(text="What is 3*6?", openai_api_key=OPENAI_API_KEY)
        assert "18" in result, "Expected result not returned from /agent/query"


    @pytest.mark.parametrize(
        "reqs_file, cand_file, num",
        [
            ("tests/data/rfp.pdf", "tests/data/candidate.pdf", 2)
        ]
    )
    def test_extract_reqs_endpoint(self, client, reqs_file, cand_file, num):
        params = ExtractReqParams(num=num).dict()

        # Call the function
        response = client.intellilang_extract_reqs(
            reqs_file, cand_file, params, openai_api_key=OPENAI_API_KEY
        )

        # Assuming the response is a text file for simplicity; adjust as needed for your actual file type
        lines = response.decode('utf-8').splitlines()
        num_lines_returned = len(lines)
        assert num_lines_returned >= num

    @pytest.mark.parametrize(
        "reqs_file, cand_files, start_idx",
        [
            ("tests/data/questions.jsonl", ["tests/data/candidate.pdf"]*2, None),
            ("tests/data/questions.jsonl", ["tests/data/candidate.pdf"]*2, 3)
        ]
    )
    def test_eval_endpoint(self, client, reqs_file, cand_files, start_idx):

        start_idx = start_idx or 1
        # Call the function

        params = EvalParams(start_idx=start_idx).dict()
        scores, evals = client.intellilang_eval(
            reqs_file, cand_files, params, openai_api_key=OPENAI_API_KEY
        )


        #check that number of lines equals the number of lines in the reqs file
        with open(reqs_file, 'r') as f:
            num = len(f.readlines())
        # For N candidates, k reqs, we are expecting:
        # - N lines containing dicts with `type = "SCORE"`
        # - N * k lines containing dicts with `type = "EVAL"`

        # extract the dict from each line
        n_score_dicts = len(scores)
        n_eval_dicts = len(evals)
        assert n_score_dicts == len(cand_files)
        assert n_eval_dicts == len(cand_files) * num
