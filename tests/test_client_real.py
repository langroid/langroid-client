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
BASE_URL = os.getenv("INTELLILANG_BASE_URL", "http://localhost:80")


@pytest.fixture
def client():
    return LangroidClient(BASE_URL)

def test_toy_endpoint(client):
    result = client.test(5)
    assert result == 25, "Expected result not returned from /test"


def test_query_endpoint(client):
    # Call the function
    result = client.agent_query(text="What is 3*6?", openai_api_key=OPENAI_API_KEY)
    assert "18" in result, "Expected result not returned from /agent/query"


def test_langroid_askdoc(client):
    doc = "tests/data/RFP/montana/montana-mobile-dev-rfp-req.pdf"
    query = "What is the job description about, in one short sentence?"
    result = client.langroid_askdoc(
        doc, query, openai_api_key=OPENAI_API_KEY
    )
    assert "mobile" in result, "Expected result not returned from /langroid/askdoc"


@pytest.mark.parametrize(
    "doc_type, reqs_file, cand_file, num",
    [
        # testing doc (not docx) since this is more demanding
        ("rfp", "tests/data/RFP/montana/montana-mobile-dev-rfp-req.pdf",
         "tests/data/RFP/montana/RFP-Responses/response.docx", 2),
        ("resume", "tests/data/job-desc.doc", "tests/data/candidate.pdf", 2),
        ("rfp", "tests/data/rfp.pdf", "tests/data/candidate.pdf", 2)
    ]
)
@pytest.mark.parametrize("rag", [False,True])
def test_extract_reqs_endpoint(
    client, doc_type, reqs_file, cand_file, num, rag
):
    params = ExtractReqParams(num=num).dict()
    fn = client.intellilang_extract_reqs_rag if rag else client.intellilang_extract_reqs
    success, response = fn(
        reqs_file, cand_file, params,
        openai_api_key=OPENAI_API_KEY, doc_type=doc_type
    )

    assert success, "Failed to process request"
    # Assuming the response is a text file for simplicity; adjust as needed for your actual file type
    lines = response.decode('utf-8').splitlines()
    num_lines_returned = len(lines)
    assert num_lines_returned >= num

@pytest.mark.parametrize(
    "reqs_file, cand_file",
    [
        # testing doc (not docx) since this is more demanding
        ("tests/data/RFP/montana/montana-mobile-dev-rfp-req.pdf",
         "tests/data/RFP/montana/RFP-Responses/response.docx"),
    ]
)
def test_extract_reqs_endpoint_err(client, reqs_file, cand_file):
    """Test that we are getting error detail"""

    params = ExtractReqParams(num=2).dict()
    fn = client.intellilang_extract_reqs
    success, response = fn(
        reqs_file, cand_file, params,
        openai_api_key="dummy", # force err
        doc_type="rfp",
    )
    print("Error: ", response)
    assert not success


@pytest.mark.parametrize(
    "reqs_file, cand_files, start_idx",
    [
        ("tests/data/questions.jsonl", ["tests/data/candidate.pdf"]*2, None),
        ("tests/data/questions.jsonl", ["tests/data/candidate.pdf"]*2, 3)
    ]
)
@pytest.mark.parametrize("rag", [False, True])
def test_eval_endpoint(client, reqs_file, cand_files, start_idx, rag):

    start_idx = start_idx or 1
    # Call the function

    params = EvalParams(start_idx=start_idx).dict()
    fn = client.intellilang_eval_rag if rag else client.intellilang_eval
    success, (scores, evals) = fn(
        reqs_file, cand_files, params, openai_api_key=OPENAI_API_KEY, doc_type="rfp"
    )


    assert success, "Failed to process request"
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
