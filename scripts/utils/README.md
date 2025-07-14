# Utility Scripts

This directory contains utility scripts that are not part of the core application but provide helpful functionality for development, debugging, and administration.

## Available Scripts

### test_jira_status.py

A utility to check or update the `posted_to_jira` status for tickets in the database.

**Usage:**
```
python utils/test_jira_status.py show [ticket_id]      # Show status for all tickets or a specific one
python utils/test_jira_status.py set [ticket_id] [0|1] # Set status for a specific ticket (0=False, 1=True)
```

This script is useful for:
- Checking which tickets have been posted to Jira
- Manually updating the posted status if needed
- Troubleshooting Jira integration issues

### test_match.py

Tests the ticket matching functionality with a sample text file.

**Usage:**
```
python utils/test_match.py path/to/text_file.txt
```

This script is useful for:
- Developing and testing the matching algorithm
- Troubleshooting ticket matching issues
- Evaluating matching performance with different inputs
