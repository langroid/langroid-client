## Langroid API Client

Python client for Langroid REST API.

## Installation

Work in a virtual environment, and use Python 3.11.

```bash
python3 -m venv .venv
. ./.venv/bin/activate
pip install langroid-client
```

## Environment Setup

Have your OpenAI API Key ready (it should be gpt-4 capable).

Set these env vars in your `.env` file placed in the root of this repo.

```bash
OPENAI_API_KEY=your-api-key-with-no-quotes
INTELLILANG_BASE_URL="https://langroid-server-zb43tal5mq-uk.a.run.app"
```

## Run the example script

Run this from the root of this repository as follows. The above environment
vars will be automatically loaded from the `.env` file.

Look into this example script to see how to use the client (also see details below).

```bash
python3 examples/example_usage.py
```

Or if you don't have an `.env` file, you can pass the vars directly at the cmd line:

```bash
INTELLILANG_BASE_URL="https://langroid-server-zb43tal5mq-uk.a.run.app" \
    OPENAI_API_KEY=your-api-key-with-no-quotes \    
    python3 examples/example_usage.py
```

# Usage of the Python API client

Before using these, first set up the `Client` object, using the `INTELLILANG_BASE_URL` env var.

Note, the API handles docs in a variety of formats-- pdf, doc, docx, txt.

```python
from langroid_client import LangroidClient
client = LangroidClient(INTELLILANG_BASE_URL)
```
### Extract requirements

```python
success, reqs_jsonl = client.intellilang_extract_reqs(
    reqs_path="path/to/requirements.pdf", # the requirements document to extract from
    candidate_path="path/to/candidate.pdf", # example of a candidate/proposal file
    params={"num": 3}, # number of requirements to extract
    openai_api_key="your-api-key",
    doc_type="rfp", # or "resume"
)
    """
    Extract requirements from a specification document.

    Args:
        reqs_path (str): Path to the requirements document.
        candidate_path (str): Path to the candidate document.
        params (Dict[str, Any]): Extraction parameters.
        openai_api_key (str): OpenAI API key.
        doc_type (str): Type of document (rfp or resume).

    Returns:
        Tuple[bool, bytes|str]:
            A tuple containing a boolean indicating success and the extracted
            requirements in jsonl format
    """
```

The returned `success` is a bool flag indicating success or not.

### Save requirements to a `jsonl` format file

```python
extracted_reqs_jsonl = "/tmp/out.jsonl"
with open(reqs_jsonl, "wb") as output_file:
    output_file.write(reqs_jsonl)
```

### Evaluate candidate docs w.r.t. extracted reqs

```python
import json
success, (scores, evals) = client.intellilang_eval(
    extracted_reqs_jsonl, # above extracted requirements jsonl file
    ["/path/to/candidate1.pdf", "/path/to/candidate2.pdf"], # list of candidate files
    params=dict(start_idx=1, cost=30.0), # leave these as a default
    openai_api_key="openai-api-key",
    doc_type="rfp",
)
"""
Evaluate candidates based on extracted requirements.

Args:
    reqs_path (str): Path to the extracted requirements file (jsonl file)
    candidate_paths (List[str]): Paths to the candidate documents.
    params (Dict[str, Any]): Evaluation parameters.
    openai_api_key (str): OpenAI API key.
    doc_type (str): Type of document (rfp or resume).

Returns:
Tuple[bool, Tuple[List[Dict[str, Any]], List[Dict[str, Any]] | str]:
            A tuple containing a boolean indicating success and tuple
of lists of scores and evaluations
"""
```

Besides the `success` flag, a tuple of two list-of-dicts is returned:

- `scores` represents the synopsis table of scores of all candidates
- `evals` represents a table containing detailed evals of all candidates
  (best to look at the example output to understand the structure)

```python
print(f"success: {success}")
# print scores
print("Scores:")
for score in scores:
    print(json.dumps(score))

# print evals
print("Evaluations:")
for eval in evals:
    print(json.dumps(eval))
```





