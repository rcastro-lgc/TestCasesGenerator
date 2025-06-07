# 🤖 ProRef — Product Refinement Automation Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**ProRef** is an intelligent assistant designed to streamline your QA and product refinement workflows by leveraging AI and integrating directly with Jira.

---

## 🚀 What It Does

- 🔄 Fetches tickets from Jira (Stories, Bugs, Tasks — excludes Spikes)
- 🧠 Analyzes and embeds tickets for semantic understanding
- 💬 Matches transcripts of refinement meetings to existing tickets
- ❓ Automatically generates pre-refinement questions (GPT-powered)
- 🧪 Test case generation from ticket context
- 📄 [Planned] Live documentation generation and update
- ☁️ [Planned] Optional posting of results back to Jira

---

## 📁 Project Structure

```
app/
├── db/         # SQLite models, sessions, and embedding storage
├── io/         # Input readers (e.g., transcript import)
├── jira/       # Jira API integration and ticket fetching
├── logic/      # Embedding, matching, generation logic
├── publish/    # Output handlers (Markdown, Jira posting)
scripts/        # CLI scripts to run specific tasks
data/           # Local data store (transcripts, outputs, DB)
tests/          # [WIP] Unit tests
```

---

## ⚙️ Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/proref.git
cd proref
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
```

3. Install dependencies and the project in editable mode:

```bash
pip install -e .
```

4. Create a `.env` file with the following variables:

```
# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USER=you@example.com
JIRA_API_TOKEN=your_jira_api_token

# Jira Query Configuration
JIRA_PROJECT=YOUR_PROJECT_KEY
JIRA_SPRINT=your-sprint-name
# You can either use the default JQL (which uses JIRA_PROJECT and JIRA_SPRINT)
# or provide your own custom JQL query:
JIRA_JQL=project = YOUR_PROJECT_KEY AND Sprint = "your-sprint-name" ORDER BY updated DESC

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key

# OpenAI Model Configuration (Optional)
OPENAI_MODEL_QUESTIONS=gpt-4-turbo
OPENAI_MODEL_TESTCASES=gpt-3.5-turbo
```

The default JQL query will be constructed using `JIRA_PROJECT` and `JIRA_SPRINT` if `JIRA_JQL` is not provided. If you need a custom query, you can set `JIRA_JQL` directly.

The `pip install -e .` command will install all necessary dependencies from `setup.py` and make the project's scripts available in your environment.

---

## �� Running Examples

- Fetch backlog tickets:
  ```bash
  python scripts/fetch_backlog.py
  ```

- Generate embeddings for tickets:
  ```bash
  python scripts/embed_tickets.py
  ```

- Match a transcript to ticket(s):
  ```bash
  python scripts/test_match.py data/transcripts/yourfile.txt
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

## 🌱 Future Improvements

- **Duplicate Prevention**: Avoid re-generating questions for tickets that have already been processed to save API tokens.
- **Test Case Generation**: Automatically generate functional test cases from ticket descriptions using AI.
- **Live Documentation**: Create and maintain a dedicated, version-controlled Markdown file for each ticket, containing its summary, key questions, and suggested tests.
- **Cross-Ticket Awareness**: Use embeddings to detect related tickets and provide impact analysis (e.g., "This change might affect...").
- **Jira Integration**: Optionally post generated questions or test cases back into the corresponding Jira ticket as comments.
- **Feature/Epic Grouping**: Generate documentation and analysis aggregated at the epic or feature level.
- **Web Dashboard**: A lightweight web interface to visually explore tickets, questions, and documentation.

---

## 📘 Philosophy

ProRef is not just automation. It's structured augmentation for QA and product teams — turning noisy backlogs and meetings into actionable, testable knowledge.

## 🤝 Contributing

Feel free to open issues or submit pull requests. This is a portfolio project showcasing AI-powered workflow automation.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

