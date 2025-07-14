# 🤖 FuzeTestAI — Product Refinement Automation Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FuzeTestAI** is an intelligent assistant designed to streamline your QA and product refinement workflows by leveraging AI and integrating directly with Jira.

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Environment Setup](#-environment-setup)
- [Gemini API Configuration](#-gemini-api-configuration)
- [Web Interface](#-web-interface)
- [Command Line Usage](#-command-line-usage)
- [Utility Scripts](#-utility-scripts)
- [Future Improvements](#-future-improvements)
- [Philosophy](#-philosophy)
- [Contributing](#-contributing)
- [License](#-license)

---

## � Features

- �🔄 **Fetch Tickets**: Retrieves tickets from Jira (Stories, Bugs, Tasks — excludes Spikes)
- 🧠 **Semantic Analysis**: Analyzes and embeds tickets for semantic understanding
- 💬 **Meeting Matching**: Matches transcripts of refinement meetings to existing tickets
- ❓ **Question Generation**: Automatically generates pre-refinement questions (AI-powered)
- 🧪 **Test Case Generation**: Creates test cases from ticket context
- 🌐 **Web Interface**: Clean UI for running scripts and viewing results in real-time
- � **Jira Integration**: Posts generated test cases back to Jira tickets
- �📄 **[Planned]** Live documentation generation and update
- ☁️ **[Planned]** Expanded Jira integration options

---

## 📁 Project Structure

```
app/
├── db/         # SQLite models, sessions, and embedding storage
├── io/         # Input readers (e.g., transcript import)
├── logic/      # Embedding, matching, generation logic
├── static/     # Web UI static assets (CSS, JS)
├── templates/  # Web UI HTML templates
├── ui.py       # Flask application for web interface
scripts/
├── fetch_backlog.py           # Fetch tickets from Jira
├── generate_questions.py      # Generate pre-refinement questions
├── generate_test_cases.py     # Generate test cases for tickets
├── test_gemini_setup.py       # Test Google Gemini API configuration
├── utils/                     # Utility scripts for development and administration
│   ├── test_jira_status.py    # Check/update Jira posting status
│   └── test_match.py          # Test ticket matching functionality
data/           # Local data store (outputs, DB)
docs/           # Documentation files
tests/          # Unit tests
```

---

## 🔧 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/FuzeTestAI.git
cd FuzeTestAI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Setup

To use FuzeTestAI, you need to set up the following environment variables:

### Required Environment Variables

```
# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USER=you@example.com
JIRA_API_TOKEN=your_jira_api_token

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Environment Variables

```
# Jira Query Configuration (use either these or custom JQL)
JIRA_PROJECT=YOUR_PROJECT_KEY
JIRA_SPRINT=your-sprint-name

# Custom JQL query (alternative to project/sprint)
# JIRA_JQL=project = YOUR_PROJECT_KEY AND Sprint = "your-sprint-name" ORDER BY updated DESC

# AI Provider Configuration
API_PROVIDER=gemini

# Model Selection
MODEL_QUESTIONS=gemini-1.5-pro
MODEL_TESTCASES=gemini-1.5-flash
```

### Setting Up Environment Variables

Create a `.env` file in the root directory of the project with your configuration.

You can test your environment setup by running:

```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'GOOGLE_API_KEY set: {bool(os.getenv(\"GOOGLE_API_KEY\"))}')"
```

---

## 🤖 Gemini API Configuration

This application uses Google Gemini as its AI provider for generating questions and test cases.

### Getting a Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create a Google account or sign in with your existing account
3. Click on "Get API key" in the menu
4. Create a new API key
5. Add the API key to your `.env` file

### Available Models

- `gemini-1.5-pro` - Best for complex reasoning and detailed output
- `gemini-1.5-flash` - Faster and more cost-effective for simpler tasks
- `gemini-1.0-pro` - Legacy model if needed

### Testing Your Gemini Setup

You can test your Gemini configuration with:

```bash
python scripts/test_gemini_setup.py
```

---

## 🌐 Web Interface

FuzeTestAI includes a web interface for running scripts and viewing results.

### Starting the Web Interface

```bash
python run_ui.py
```

Then access the UI at http://localhost:5000

### Web Interface Features

- Run and monitor scripts with a clean user interface
- View real-time output of running scripts
- View generated questions and test cases in a formatted display
- Stop running scripts when needed
- Send test cases to Jira

### Workflow

1. First, run "Fetch Backlog" to download tickets from Jira
2. Then run "Generate Questions" to create pre-refinement questions for each ticket
3. Finally, run "Generate Test Cases" to create test cases for each ticket

---

## 💻 Command Line Usage

FuzeTestAI can also be used from the command line:

- Fetch backlog tickets:
  ```bash
  python scripts/fetch_backlog.py
  ```

- Generate embeddings for tickets:
  ```bash
  python scripts/embed_tickets.py
  ```

- Generate QA questions:
  ```bash
  python scripts/generate_questions.py
  ```

- Interactive chat with your tickets:
  ```bash
  python scripts/chat.py
  ```

---

## 🛠 Utility Scripts

The `scripts/utils/` directory contains utility scripts for development, debugging, and administration:

### test_jira_status.py

A utility to check or update the `posted_to_jira` status for tickets in the database.

**Usage:**
```
python scripts/utils/test_jira_status.py show [ticket_id]      # Show status for all tickets or a specific one
python scripts/utils/test_jira_status.py set [ticket_id] [0|1] # Set status for a specific ticket (0=False, 1=True)
```

### test_match.py

Tests the ticket matching functionality with a sample text file.

**Usage:**
```
python scripts/utils/test_match.py path/to/text_file.txt
```

---

## 🌱 Future Improvements

- **Duplicate Prevention**: Avoid re-generating questions for tickets that have already been processed to save API tokens.
- **Live Documentation**: Create and maintain a dedicated, version-controlled Markdown file for each ticket, containing its summary, key questions, and suggested tests.
- **Cross-Ticket Awareness**: Use embeddings to detect related tickets and provide impact analysis (e.g., "This change might affect...").
- **Expanded Jira Integration**: Additional options for posting generated content back to Jira.
- **Feature/Epic Grouping**: Generate documentation and analysis aggregated at the epic or feature level.
- **Enhanced Web Dashboard**: Additional features for the web interface.

---

## 📘 Philosophy

FuzeTestAI is not just automation. It's structured augmentation for QA and product teams — turning noisy backlogs and meetings into actionable, testable knowledge.

---

## 🤝 Contributing

Feel free to open issues or submit pull requests. This is a portfolio project showcasing AI-powered workflow automation.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
