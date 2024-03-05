from langroid_client import LangroidClient
import json

BASE_URL = "http://localhost:80"

def main():
    # Initialize the client with the API's base URL
    client = LangroidClient(BASE_URL)

    # Example usage of the /test endpoint
    x = 5
    print("Calling /test endpoint...")
    result = client.test(x)
    print(f"Result from /test: {result}")

    # # Example usage of the /extract endpoint
    reqs_path = "tests/data/rfp.pdf"
    candidate_path = "tests/data/candidate.pdf"
    params = dict(num=3)

    print("Calling /extract endpoint...")
    extracted_reqs = client.intellilang_extract_reqs(reqs_path, candidate_path, params)

    # Assuming the response_content is a binary stream of a .jsonl file
    # Let's save this content to a file first
    extracted_reqs_jsonl = "/tmp/out.jsonl"
    with open(extracted_reqs_jsonl, "wb") as output_file:
        output_file.write(extracted_reqs)

    # Now, let's read the .jsonl file and process the JSON objects
    with open(extracted_reqs_jsonl, "r") as jsonl_file:
        for line in jsonl_file:
            json_object = json.loads(line)
            # Process each JSON object here
            print(json_object)

    print("Calling /eval endpoint...")
    # evaluate candidates based on extracted reqs
    # (simply repeat one candidate for testing)

    # dump output to a file
    scores, evals = client.intellilang_eval(extracted_reqs_jsonl, [candidate_path]*2)

    # print scores
    print("Scores:")
    for score in scores:
        print(json.dumps(score))

    # print evals
    print("Evaluations:")
    for eval in evals:
        print(json.dumps(eval))




if __name__ == "__main__":
    main()
