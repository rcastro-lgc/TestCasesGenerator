# ProRef UI

A simple web interface for running ProRef scripts and viewing results.

## Features

- Run and monitor scripts with a clean user interface
- View real-time output of running scripts
- View generated questions and test cases in a formatted display
- Stop running scripts when needed
- Monitor script status

## Setup

1. Make sure you have all the required dependencies installed:

```bash
pip install -r requirements.txt
```

2. Make sure you have all necessary environment variables set in your `.env` file:

```
GOOGLE_API_KEY=your-google-api-key
JIRA_BASE_URL=your-jira-url
JIRA_USER=your-jira-username
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT=your-jira-project
JIRA_SPRINT=your-sprint-name
```

## Usage

1. Run the UI:

```bash
python run_ui.py
```

2. Open a web browser and navigate to:

```
http://localhost:5000
```

3. Use the interface to:
   - Fetch tickets from Jira
   - Generate pre-refinement questions for tickets
   - Generate test cases for tickets
   - View the results

## Workflow

1. First, run "Fetch Backlog" to download tickets from Jira
2. Then run "Generate Questions" to create pre-refinement questions for each ticket
3. Finally, run "Generate Test Cases" to create test cases for each ticket

## Viewing Results

- After generating questions or test cases, click the "View Questions" or "View Test Cases" buttons to see the results
- Results are stored in Markdown files in the `data/questions` and `data/test_cases` directories
