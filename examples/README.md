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

```bash
python3 examples/example_usage.py
```

Or if you don't have an `.env` file, you can pass the vars directly at the cmd line:

```bash
INTELLILANG_BASE_URL="https://langroid-server-zb43tal5mq-uk.a.run.app" \
    OPENAI_API_KEY=your-api-key-with-no-quotes \    
    python3 examples/example_usage.py
```


