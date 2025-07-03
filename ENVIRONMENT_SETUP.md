# ProRef UI - Environment Setup

This file explains how to set up your environment variables for the ProRef UI.

## Required Environment Variables

To use the ProRef UI, you need to set the following environment variables:

```
GOOGLE_API_KEY=your-google-api-key
JIRA_BASE_URL=your-jira-url
JIRA_USER=your-jira-username
JIRA_API_TOKEN=your-jira-api-token
```

Plus either:
```
JIRA_PROJECT=your-jira-project
JIRA_SPRINT=your-sprint-name
```

Or:
```
JIRA_JQL=your-custom-jql-query
```

## Setting Up Environment Variables

### Option 1: Using a .env file

Create a `.env` file in the root directory of the project with the following content:

```
GOOGLE_API_KEY=your-google-api-key
JIRA_BASE_URL=your-jira-url
JIRA_USER=your-jira-username
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT=your-jira-project
JIRA_SPRINT=your-sprint-name
```

### Option 2: Setting environment variables in your terminal

```bash
export GOOGLE_API_KEY=your-google-api-key
export JIRA_BASE_URL=your-jira-url
export JIRA_USER=your-jira-username
export JIRA_API_TOKEN=your-jira-api-token
export JIRA_PROJECT=your-jira-project
export JIRA_SPRINT=your-sprint-name
```

## Testing Your Environment

You can test your environment setup by running:

```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'GOOGLE_API_KEY set: {bool(os.getenv(\"GOOGLE_API_KEY\"))}')"
```

If the output is `GOOGLE_API_KEY set: True`, your environment is set up correctly.

## Running the UI

Once your environment is set up, you can run the UI with:

```bash
python3 run_ui.py
```

Then access the UI at http://localhost:5000
