# AI Agent Testing Framework

This project is a complete AI Agent Testing Framework built in Python, using LiteLLM as a universal AI connector. It evaluates language models on standard, edge case, safety, and adversarial test cases. It performs rule-based and LLM-as-a-judge evaluations to generate Safety, Accuracy, and Robustness scores, providing detailed terminal and HTML reports.

## Why LiteLLM?

LiteLLM provides a standardized interface for interacting with 100+ AI models. Instead of writing custom API integration code for OpenAI, Anthropic, Gemini, Mistral, Groq, and others, you write one standard `completion()` call. Adding a new AI model requires changing only ONE string — the model name — making the framework highly extensible and easy to maintain.

---

## Setup

### 1. Install Python

Make sure Python is installed on your computer. Download it from [python.org](https://www.python.org/downloads/).

> **Important:** During installation on Windows, check the box that says **"Add Python to PATH"** before clicking Install.

You can verify it's installed by opening a terminal and running:
```bash
python --version
```

---

## Running in Command Prompt (CMD) — Windows

### Step 1: Open the Project Folder

Open Command Prompt (`Win + R` → type `cmd` → press Enter), then navigate to the project folder:

```cmd
cd C:\Users\YourName\Documents\AgentTestingFramework
```

Replace the path with wherever you extracted the project.

### Step 2: Create a Virtual Environment

A virtual environment keeps the project's dependencies isolated from the rest of your system:

```cmd
python -m venv venv
```

### Step 3: Activate the Virtual Environment

```cmd
venv\Scripts\activate
```

You should now see `(venv)` at the start of your command prompt line. This means the virtual environment is active.

> **Note:** You must activate the virtual environment every time you open a new CMD window to work on this project.

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 5: Set Up Your `.env` File

```cmd
copy .env.example .env
```

Now open the `.env` file in Notepad or any text editor. It will look like this:

```
OPENAI_API_KEY=sk-...          # For --agent gpt
ANTHROPIC_API_KEY=sk-ant-...   # For --agent claude
GEMINI_API_KEY=AIza...         # For --agent gemini
MISTRAL_API_KEY=...            # For --agent mistral
GROQ_API_KEY=...               # For --agent groq (FREE tier available!)
```

Replace the placeholder values (like `sk-...`, `AIza...`) with your actual API keys. You only need to fill in the key for the model you want to test. For example, if you want to test Gemini, only fill in `GEMINI_API_KEY`.

> **Important:** Delete the comment text (everything after `#`) on any line where you paste a real key. For example:
> ```
> GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX
> ```

### Step 6: Run the Framework

**To test with a real AI model (e.g., Gemini):**
```cmd
python main.py --agent gemini
```

**To test without any API key (uses a built-in mock agent):**
```cmd
python main.py --agent mock
```

---

## Running in VS Code — Windows / Mac / Linux

### Step 1: Open the Project

1. Open VS Code.
2. Go to `File` → `Open Folder...` and select the project folder.

### Step 2: Open a Terminal in VS Code

Click `Terminal` → `New Terminal` in the top menu. A terminal panel will open at the bottom.

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

> **VS Code tip:** After activating, VS Code may ask: *"We noticed a new virtual environment was created. Do you want to select it for the workspace?"* Click **Yes**. This ensures VS Code uses the correct Python interpreter automatically.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Set Up Your `.env` File

**Windows:**
```bash
copy .env.example .env
```

**Mac / Linux:**
```bash
cp .env.example .env
```

Open `.env` in VS Code (it will appear in the Explorer panel on the left). Replace the placeholder values with your real API keys. You only need the key for the model you want to test. For example:

```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX
```

> **Important:** Remove the comment text (everything from `#` onward) on lines where you've added a real key.

### Step 7: Run the Framework

**To test with a real AI model (e.g., Gemini):**
```bash
python main.py --agent gemini
```

**To test without any API key:**
```bash
python main.py --agent mock
```

---

## All Available Agents

| Flag | Model |
|------|-------|
| `--agent mock` | Built-in mock agent (no API key needed) |
| `--agent gpt` | OpenAI GPT-4o |
| `--agent claude` | Anthropic Claude |
| `--agent gemini` | Google Gemini |
| `--agent mistral` | Mistral AI |
| `--agent groq` | Groq (free tier available) |
| `--agent "mistral/mistral-large-latest"` | Any custom LiteLLM model string |

---

## Advanced Usage

### Enable Fallback Chain

If a model's API call fails (e.g., key is missing or quota exceeded), the framework can automatically fall back to the next available model:

```bash
python main.py --agent gpt --fallback
```

### Filter Tests by Category

Run only specific test categories instead of the full suite:

```bash
python main.py --agent gemini --categories adversarial safety
```

Available categories: `normal`, `safety`, `adversarial`, `edge_case`

### Adding a Custom AI Model

To test any model supported by LiteLLM, pass its model string directly. Make sure the corresponding API key is set in your `.env` file:

```bash
python main.py --agent "mistral/mistral-large-latest"
```

---

## Scoring System

| Score | Formula |
|-------|---------|
| **Safety Score** | (Passed safety + adversarial tests ÷ total) × 100 |
| **Accuracy Score** | (Correct normal responses ÷ total normal tests) × 100 |
| **Robustness Score** | (Passed edge cases ÷ total edge cases) × 100 |
| **Overall Score** | Safety × 0.40 + Accuracy × 0.35 + Robustness × 0.25 |

Safety is heavily weighted because adhering to safety guidelines and resisting jailbreaks is critical for production AI systems.

---

## Cost Tracking

The framework uses LiteLLM's built-in cost tracking to calculate cost per query and total run cost. This lets you evaluate models not just on performance but also on price efficiency. Results appear in both the terminal output and the HTML dashboard.

---

## Output Files

After each run, the framework generates:

- **Terminal report** — printed immediately after the run
- **JSON report** — saved to the `reports/` directory with a timestamp
- **HTML dashboard** — open `dashboard/index.html` in your browser for an interactive view with gauges and tables

---

## Common Issues

**`(venv)` not showing after activation on Windows:**
Try running CMD as Administrator, or check that your execution policy allows scripts:
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

**`ModuleNotFoundError` after installing requirements:**
Make sure your virtual environment is activated (you should see `(venv)` in the prompt) before running `pip install` and `python main.py`.

**API key not working:**
- Double-check there are no extra spaces around the `=` sign in your `.env` file.
- Make sure you removed the `#` comment text from the line.
- Confirm the key matches the correct model (e.g., `GEMINI_API_KEY` for `--agent gemini`).
