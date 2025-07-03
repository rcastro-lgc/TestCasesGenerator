import os
import threading
import io
import sys
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
from contextlib import redirect_stdout
import traceback

# This file is the consolidated version of ui.py and ui_fixed.py
# It includes improved error handling and environment checks for Google Gemini

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

# Store process status
process_status = {
    'fetch_backlog': {'status': 'idle', 'output': [], 'start_time': None, 'end_time': None},
    'generate_questions': {'status': 'idle', 'output': [], 'start_time': None, 'end_time': None},
    'generate_test_cases': {'status': 'idle', 'output': [], 'start_time': None, 'end_time': None}
}

# Store active threads
active_threads = {}

# Function to check environment variables
def check_environment():
    from app.config import API_PROVIDER
    
    required_vars = {
        'JIRA_BASE_URL': 'Jira Base URL',
        'JIRA_USER': 'Jira Username',
        'JIRA_API_TOKEN': 'Jira API Token',
        'GOOGLE_API_KEY': 'Google API Key'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{description} ({var})")
    
    if not os.getenv('JIRA_JQL') and not (os.getenv('JIRA_PROJECT') or os.getenv('JIRA_SPRINT')):
        missing_vars.append("Either JIRA_JQL or both JIRA_PROJECT and JIRA_SPRINT must be set")
    
    return missing_vars

# Function for fetch_backlog logic
def run_fetch_backlog():
    # Check environment first
    missing_vars = check_environment()
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Dynamically import here to handle environment variable issues gracefully
    from dotenv import load_dotenv
    from app.db.model import init_db
    from app.db.save import save_or_update_ticket
    from app.io.adf_parser import parse_adf_to_text
    import requests
    
    load_dotenv()
    
    # Required Jira configuration
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_USER = os.getenv("JIRA_USER")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

    # JQL configuration - can be set directly or constructed from project and sprint
    JIRA_PROJECT = os.getenv("JIRA_PROJECT")
    JIRA_SPRINT = os.getenv("JIRA_SPRINT")
    JIRA_JQL = os.getenv("JIRA_JQL")

    if not JIRA_JQL:
        if not all([JIRA_PROJECT, JIRA_SPRINT]):
            raise ValueError("Either JIRA_JQL or both JIRA_PROJECT and JIRA_SPRINT must be set in .env")
        JQL = f'project = {JIRA_PROJECT} AND Sprint = "{JIRA_SPRINT}" ORDER BY updated DESC'
    else:
        JQL = JIRA_JQL
        
    print("🔄 Initializing database...")
    init_db()

    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USER, JIRA_API_TOKEN)
    params = {
        "jql": JQL,
        "fields": "summary,description,status,updated, issuetype",
        "maxResults": 150
    }

    print("📡 Querying tickets from Jira...")
    response = requests.get(url, headers=headers, params=params, auth=auth)

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        for issue in issues:
            key = issue["key"]
            fields = issue["fields"]

            description = fields.get("description")
            if isinstance(description, dict):
                description = parse_adf_to_text(description)
            elif description is None:
                description = ""

            updated_str = fields.get("updated")
            updated_at = None
            if updated_str:
                updated_at = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%S.%f%z")

            issue_type = fields.get("issuetype", {}).get("name", "").lower()

            if issue_type == "spike":
                print(f"⏭️  Skipping SPIKE: {key}")
                continue

            ticket_data = {
                "id": key,
                "jira_key": key,
                "title": fields.get("summary"),
                "description": description,
                "issue_type": issue_type,
                "status": fields.get("status", {}).get("name", ""),
                "updated_at": updated_at
            }

            save_or_update_ticket(ticket_data)
            print(f"✅ Saved: [{key}] {fields['summary']}")
        
        print(
            f"✅ Total tickets processed (excluding Spikes): {len([i for i in issues if i['fields'].get('issuetype', {}).get('name', '').lower() != 'spike'])}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

# Function for generate_questions logic
def run_generate_questions():
    # Check environment first
    missing_vars = check_environment()
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Dynamically import here to handle environment variable issues gracefully
    from dotenv import load_dotenv
    from app.db.model import SessionLocal, Ticket
    from app.logic.question_generator import generate_questions
    
    load_dotenv()
    
    # Output path
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "questions", "questions_by_ticket.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Get tickets that haven't been processed yet
    session = SessionLocal()
    tickets = session.query(Ticket).filter(
        Ticket.issue_type != "Spike",
        Ticket.questions_generated != True
    ).all()

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, ticket in enumerate(tickets):
            print(f"🔄 Generating questions for {ticket.jira_key} ({idx+1}/{len(tickets)})")
            questions = generate_questions(ticket)

            f.write(f"## {ticket.jira_key} - {ticket.title}\n")
            f.write(f"**Type:** {ticket.issue_type}\n\n")

            if questions:
                f.write("**Generated questions:**\n")
                for q in questions:
                    f.write(f"- {q}\n")
                # Mark ticket as processed
                ticket.questions_generated = True
                session.add(ticket)
            else:
                f.write("_No questions generated._\n")

            f.write("\n---\n\n")

    session.commit()
    session.close()
    print(f"✅ Preguntas generadas y guardadas en: {output_path}")

# Function for generate_test_cases logic
def run_generate_test_cases():
    # Check environment first
    missing_vars = check_environment()
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Dynamically import here to handle environment variable issues gracefully
    from dotenv import load_dotenv
    from app.db.model import SessionLocal, Ticket
    from app.logic.test_case_generator import generate_test_cases
    
    load_dotenv()
    
    # Output path
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "test_cases", "test_cases_by_ticket.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Get all valid tickets
    session = SessionLocal()
    tickets = session.query(Ticket).filter(
        Ticket.test_cases_generated == False,
        Ticket.description != None,
        Ticket.title != None
    ).all()
    session.close()

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, ticket in enumerate(tickets, 1):
            print(f"🧪 Generating test cases for {ticket.jira_key} ({idx}/{len(tickets)})")
            test_cases = generate_test_cases(ticket)

            f.write(f"## {ticket.jira_key} - {ticket.title}\n")
            f.write(f"**Type:** {ticket.issue_type}\n\n")

            if test_cases:
                current_block = []
                test_case_count = 0

                for line in test_cases:
                    line = line.strip()
                    if not line:
                        continue

                    current_block.append(line)

                    if len(current_block) == 3:
                        scenario = action = expected = "(not detected)"

                        for item in current_block:
                            lower = item.lower().replace("**", "").replace("-", "").strip()
                            if lower.startswith("scenario"):
                                scenario = item.split(":", 1)[-1].strip()
                            elif lower.startswith("action"):
                                action = item.split(":", 1)[-1].strip()
                            elif "expected behavior" in lower:
                                expected = item.split(":", 1)[-1].strip()

                        test_case_count += 1
                        f.write(f"### ✅ Test Case {test_case_count}\n")
                        f.write(f"- **Scenario:** _{scenario}_\n")
                        f.write(f"- **Action:** _{action}_\n")
                        f.write(f"- **Expected behavior:** _{expected}_\n")
                        f.write("\n---\n\n")

                        current_block = []

                if test_case_count > 0:
                    session = SessionLocal()
                    db_ticket = session.query(Ticket).filter_by(jira_key=ticket.jira_key).first()
                    if db_ticket:
                        db_ticket.test_cases_generated = True
                        session.commit()
                    session.close()
                else:
                    f.write("_No valid test cases detected._\n\n---\n\n")

            else:
                f.write("_No test cases generated._\n\n---\n\n")

    print(f"✅ Test cases saved to: {output_path}")

# Dictionary mapping script names to their functions
script_functions = {
    'fetch_backlog': run_fetch_backlog,
    'generate_questions': run_generate_questions,
    'generate_test_cases': run_generate_test_cases
}

def run_script(script_name):
    # Reset status
    process_status[script_name]['status'] = 'running'
    process_status[script_name]['output'] = []
    process_status[script_name]['start_time'] = datetime.now()
    process_status[script_name]['end_time'] = None
    
    # Create a string buffer to capture stdout
    stdout_buffer = io.StringIO()
    
    try:
        # Redirect stdout to our buffer
        with redirect_stdout(stdout_buffer):
            # Call the appropriate function
            script_functions[script_name]()
        
        # Get output from buffer
        output = stdout_buffer.getvalue()
        for line in output.splitlines():
            process_status[script_name]['output'].append(line.strip())
        
        # Update status to completed
        process_status[script_name]['status'] = 'completed'
        
    except Exception as e:
        # Capture the error and traceback
        error_message = f"Error executing {script_name}: {str(e)}"
        process_status[script_name]['output'].append(error_message)
        
        # Check for API errors
        error_str = str(e).lower()
        
        # Gemini-specific errors
        if "google" in error_str and ("api key" in error_str or "authentication" in error_str or "credentials" in error_str):
            process_status[script_name]['output'].append("")
            process_status[script_name]['output'].append("🚫 Google API Key Error Detected")
            process_status[script_name]['output'].append("This error occurs when your Google API key is invalid or has not been properly set up.")
        elif "google" in error_str and ("quota" in error_str or "rate" in error_str or "limit" in error_str):
            process_status[script_name]['output'].append("")
            process_status[script_name]['output'].append("🚫 Google API Quota Error Detected")
            process_status[script_name]['output'].append("This error occurs when your Google API key has exceeded its quota or rate limits.")
        
        # Add traceback for debugging
        tb = traceback.format_exc()
        for line in tb.splitlines():
            process_status[script_name]['output'].append(line)
            
        process_status[script_name]['status'] = 'failed'
    
    finally:
        # Update the end time
        process_status[script_name]['end_time'] = datetime.now()
        
        # Remove from active threads
        if script_name in active_threads:
            del active_threads[script_name]

@app.route('/')
def home():
    # Check environment variables
    missing_vars = check_environment()
    return render_template('index.html', process_status=process_status, missing_vars=missing_vars)

@app.route('/run/<script_name>', methods=['POST'])
def run(script_name):
    if script_name not in process_status:
        return jsonify({'error': 'Invalid script name'}), 400
    
    # Check if already running
    if process_status[script_name]['status'] == 'running':
        return jsonify({'error': 'Script already running'}), 400
    
    # Start script in a thread
    thread = threading.Thread(target=run_script, args=(script_name,))
    thread.daemon = True
    thread.start()
    
    # Store the thread
    active_threads[script_name] = thread
    
    return jsonify({'status': 'started'})

@app.route('/status/<script_name>')
def status(script_name):
    if script_name not in process_status:
        return jsonify({'error': 'Invalid script name'}), 400
    
    return jsonify(process_status[script_name])

@app.route('/status/all')
def status_all():
    return jsonify(process_status)

@app.route('/stop/<script_name>', methods=['POST'])
def stop(script_name):
    # Note: We can't directly stop a thread in Python safely
    # This function is just for API consistency, but will only
    # mark the process as stopped. The thread will continue
    # but its results will be ignored
    
    if script_name not in active_threads:
        return jsonify({'error': 'No active process found'}), 400
    
    process_status[script_name]['status'] = 'stopped'
    process_status[script_name]['end_time'] = datetime.now()
    
    # We can't really stop the thread, but we can remove it from active_threads
    del active_threads[script_name]
    
    return jsonify({'status': 'stopped'})

@app.route('/view_output/<output_type>')
def view_output(output_type):
    if output_type == 'questions':
        file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'questions', 'questions_by_ticket.md'))
    elif output_type == 'test_cases':
        file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'test_cases', 'test_cases_by_ticket.md'))
    else:
        return "Invalid output type", 400
    
    if not os.path.exists(file_path):
        return f"Output file not found: {file_path}", 404
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    return render_template('output.html', content=content, output_type=output_type)

def start():
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    start()
