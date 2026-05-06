# Architecture

```text
User → main.py → agents.py (LiteLLM) → Any AI API
                     ↓
              framework.py (test runner)
                     ↓
              evaluator.py (rule-based + LLM judge)
                     ↓  
              adversarial.py (dynamic prompts)
                     ↓
              reporter.py → terminal report + JSON + HTML dashboard
```

## Components

- **`main.py`**: The CLI entry point. Parses arguments, sets up the environment, and triggers the framework.
- **`src/agents.py`**: Contains the Litellm agent interface and configuration. Handles model mapping, API calls, error handling for missing keys, and fallbacks. Also implements the `MockAgent`.
- **`src/framework.py`**: The core testing engine. Loads test cases, manages the test loop, tracks time and cost, coordinates evaluation, and computes final scores.
- **`src/evaluator.py`**: Runs evaluations on the responses. Performs rule-based checks (refusal detection, injection resistance, safety, etc.) and LLM-as-a-judge scoring using Litellm.
- **`src/adversarial.py`**: Manages adversarial testing logic. Automatically generates dynamic adversarial prompts from templates.
- **`src/reporter.py`**: Generates human-readable terminal reports using `rich`, saves test results to JSON, and injects the JSON data into the HTML dashboard.
- **`dashboard/index.html`**: A standalone HTML file containing visual components (gauges, tables) to review test results.
