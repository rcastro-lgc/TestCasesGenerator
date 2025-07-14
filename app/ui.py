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
    'fetch_backlog': {
        'status': 'idle', 
        'output': [], 
        'start_time': None, 
        'end_time': None, 
        'tickets': [],
        'custom_jira_filter': None
    },
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

    # JIRA_JQL check is no longer needed as we use the UI filter

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
    
    # Check if we have a custom filter from the UI
    custom_filter = process_status['fetch_backlog'].get('custom_jira_filter')
    if custom_filter:
        JQL = custom_filter
        # Reset the custom filter after using it
        process_status['fetch_backlog']['custom_jira_filter'] = None
    else:
        # No custom filter provided, use project and sprint as fallback
        if not all([JIRA_PROJECT, JIRA_SPRINT]):
            raise ValueError("No Jira filter provided. Please enter a JQL filter in the 'Jira Filter' field.")
        JQL = f'project = {JIRA_PROJECT} AND Sprint = "{JIRA_SPRINT}" ORDER BY updated DESC'
        
    print("🔄 Initializing database...")
    init_db()

    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if JIRA_USER is None or JIRA_API_TOKEN is None:
        raise ValueError("JIRA_USER and JIRA_API_TOKEN must not be None")
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
        # Clear any previous tickets
        process_status['fetch_backlog']['tickets'] = []

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

            # Store the ticket data in our process status
            process_status['fetch_backlog']['tickets'].append({
                "jira_key": key,
                "title": fields.get("summary"),
                "description": description,  # Include description for UI display
                "issue_type": issue_type,
                "status": fields.get("status", {}).get("name", "")
            })

            save_or_update_ticket(ticket_data)
            print(f"✅ Saved: [{key}] {fields['summary']}")

        print(
            f"✅ Total tickets processed (excluding Spikes): {len([i for i in issues if i['fields'].get('issuetype', {}).get('name', '').lower() != 'spike'])}")
        print(f"✅ Total tickets in process_status: {len(process_status['fetch_backlog']['tickets'])}")
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
                setattr(ticket, 'questions_generated', True)
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
    from app.db.save import save_test_case

    load_dotenv()

    # Get all valid tickets
    session = SessionLocal()
    tickets = session.query(Ticket).filter(
        Ticket.test_cases_generated == False,
        Ticket.description != None,
        Ticket.title != None
    ).all()
    session.close()

    total_tickets = len(tickets)
    tickets_processed = 0
    total_test_cases = 0

    for idx, ticket in enumerate(tickets, 1):
        print(f"🧪 Generating test cases for {ticket.jira_key} ({idx}/{total_tickets})")
        test_cases = generate_test_cases(ticket)

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
                    total_test_cases += 1

                    # Save test case to database
                    try:
                        save_test_case(ticket.id, scenario, action, expected)
                        print(f"✅ Test case saved to database for ticket {ticket.jira_key}")
                    except Exception as e:
                        print(f"❌ Error saving test case to database: {str(e)}")

                    current_block = []
            
            if test_case_count > 0:
                tickets_processed += 1
                session = SessionLocal()
                db_ticket = session.query(Ticket).filter_by(jira_key=ticket.jira_key).first()
                if db_ticket:
                    setattr(db_ticket, 'test_cases_generated', True)
                    session.commit()
                session.close()
                print(f"✅ Generated {test_case_count} test cases for ticket {ticket.jira_key}")
            else:
                print(f"⚠️ No valid test cases detected for ticket {ticket.jira_key}")
        else:
            print(f"⚠️ No test cases generated for ticket {ticket.jira_key}")

    print(f"✅ Test cases generation completed: {total_test_cases} test cases for {tickets_processed} tickets")

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

    # Reset tickets list for fetch_backlog
    if script_name == 'fetch_backlog':
        process_status[script_name]['tickets'] = []
        print(f"Reset tickets list for {script_name}")

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

        if script_name == 'fetch_backlog':
            # Verify tickets were properly stored (diagnostic)
            if not process_status[script_name]['tickets']:
                process_status[script_name]['output'].append("⚠️ Warning: No tickets were found or added to the process status.")

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

    # Get tickets with their test cases
    tickets_data = []
    from app.db.model import SessionLocal, Ticket, TestCase

    # Only show tickets from the current fetch
    if process_status['fetch_backlog']['tickets']:
        # Get tickets from the current fetch
        jira_keys = [ticket['jira_key'] for ticket in process_status['fetch_backlog']['tickets']]

        # Get details and test cases for these tickets
        session = SessionLocal()
        tickets = session.query(Ticket).filter(Ticket.jira_key.in_(jira_keys)).all()

        for ticket in tickets:
            # Get test cases for this ticket
            test_cases = session.query(TestCase).filter(TestCase.ticket_id == ticket.id).all()

            ticket_data = {
                'jira_key': ticket.jira_key,
                'title': ticket.title,
                'description': ticket.description,
                'issue_type': ticket.issue_type,
                'status': ticket.status,
                'has_test_cases': ticket.test_cases_generated,
                'test_cases': []
            }

            # Add test cases if any
            for test_case in test_cases:
                ticket_data['test_cases'].append({
                    'id': test_case.id,
                    'scenario': test_case.scenario,
                    'action': test_case.action,
                    'expected_behavior': test_case.expected_behavior,
                    'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.created_at is not None else ''
                })

            tickets_data.append(ticket_data)

        session.close()

    return render_template('index.html', process_status=process_status, missing_vars=missing_vars, 
                           tickets_data=tickets_data)

@app.route('/run/<script_name>', methods=['POST'])
def run(script_name):
    if script_name not in process_status:
        return jsonify({'error': 'Invalid script name'}), 400

    # Check if already running
    if process_status[script_name]['status'] == 'running':
        return jsonify({'error': 'Script already running'}), 400
    
    # Check if we have a custom Jira filter for fetch_backlog
    if script_name == 'fetch_backlog' and request.is_json:
        data = request.get_json()
        # Check both parameter names for compatibility
        custom_jira_filter = data.get('jira_filter') or data.get('jql')
        if custom_jira_filter:
            # Store the custom filter in process_status for the run_script function to use
            process_status[script_name]['custom_jira_filter'] = custom_jira_filter

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

    # For fetch_backlog, include the tickets in the response
    if script_name == 'fetch_backlog':
        # Always include ticket data for direct UI update, regardless of status
        response_data = {
            'status': process_status[script_name]['status'],
            'output': process_status[script_name]['output'],
            'start_time': process_status[script_name]['start_time'].isoformat() if process_status[script_name]['start_time'] else None,
            'end_time': process_status[script_name]['end_time'].isoformat() if process_status[script_name]['end_time'] else None,
            'tickets': process_status[script_name]['tickets']
        }
        return jsonify(response_data)

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

        if not os.path.exists(file_path):
            return f"Output file not found: {file_path}", 404

        with open(file_path, 'r') as f:
            content = f.read()

        return render_template('output.html', content=content, output_type=output_type)

    elif output_type == 'test_cases':
        from app.db.model import SessionLocal, Ticket, TestCase

        # Get test cases from database
        session = SessionLocal()
        test_cases_db = session.query(Ticket, TestCase).join(TestCase, Ticket.id == TestCase.ticket_id).all()
        session.close()

        if not test_cases_db:
            return "No test cases found in the database.", 404

        # Create a dictionary to organize test cases by ticket
        test_cases_by_ticket = {}
        for ticket, test_case in test_cases_db:
            if ticket.jira_key not in test_cases_by_ticket:
                test_cases_by_ticket[ticket.jira_key] = {
                    'ticket': {
                        'jira_key': ticket.jira_key,
                        'title': ticket.title,
                        'issue_type': ticket.issue_type,
                        'id': ticket.id
                    },
                    'test_cases': []
                }
            test_cases_by_ticket[ticket.jira_key]['test_cases'].append({
                'id': test_case.id,
                'scenario': test_case.scenario,
                'action': test_case.action,
                'expected_behavior': test_case.expected_behavior,
                'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.created_at else ''
            })

        # Create minimal dummy content with just ticket headers - test cases will come only from db_test_cases
        dummy_content = ""
        for jira_key, data in test_cases_by_ticket.items():
            dummy_content += f"## {jira_key} - {data['ticket']['title']}\n\n"
            # No type information or test cases in dummy_content - they will be displayed from db_test_cases only

        # Pass both the dummy content and the database test cases
        return render_template('output.html', content=dummy_content, output_type=output_type, 
                              db_test_cases=test_cases_by_ticket)

    else:
        return "Invalid output type", 400

# Function to generate test cases for a single ticket
def generate_test_cases_for_ticket(ticket_id):
    # Check environment first
    missing_vars = check_environment()
    if missing_vars:
        return {"success": False, "message": f"Missing required environment variables: {', '.join(missing_vars)}"}

    # Dynamically import here to handle environment variable issues gracefully
    from dotenv import load_dotenv
    from app.db.model import SessionLocal, Ticket
    from app.logic.test_case_generator import generate_test_cases
    from app.db.save import save_test_case

    load_dotenv()

    # Get the specific ticket
    session = SessionLocal()
    ticket = session.query(Ticket).filter(Ticket.jira_key == ticket_id).first()
    session.close()

    if not ticket:
        return {"success": False, "message": f"Ticket {ticket_id} not found"}

    # Generate test cases for this ticket
    test_cases = generate_test_cases(ticket)
    test_case_count = 0

    if test_cases:
        current_block = []

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

                # Save test case to database
                try:
                    save_test_case(ticket.id, scenario, action, expected)
                except Exception as e:
                    return {"success": False, "message": f"Error saving test case: {str(e)}"}

                current_block = []

        if test_case_count > 0:
            session = SessionLocal()
            db_ticket = session.query(Ticket).filter_by(jira_key=ticket.jira_key).first()
            if db_ticket:
                # Set the test_cases_generated attribute to True
                setattr(db_ticket, 'test_cases_generated', True)
                session.commit()
            session.close()
            return {"success": True, "message": f"Generated {test_case_count} test cases for ticket {ticket.jira_key}", "count": test_case_count}
        else:
            return {"success": False, "message": f"No valid test cases detected for ticket {ticket.jira_key}"}
    else:
        return {"success": False, "message": f"No test cases could be generated for ticket {ticket.jira_key}"}

@app.route('/generate_test_cases/<ticket_id>', methods=['POST'])
def generate_test_cases_endpoint(ticket_id):
    result = generate_test_cases_for_ticket(ticket_id)
    return jsonify(result)

@app.route('/get_test_cases/<ticket_id>')
def get_test_cases(ticket_id):
    from app.db.model import SessionLocal, Ticket, TestCase

    # Get test cases for the specified ticket
    session = SessionLocal()
    ticket = session.query(Ticket).filter(Ticket.jira_key == ticket_id).first()

    if not ticket:
        return jsonify({"success": False, "message": f"Ticket {ticket_id} not found"}), 404

    test_cases = session.query(TestCase).filter(TestCase.ticket_id == ticket.id).all()
    session.close()

    # Format test cases for the response
    test_cases_data = []
    for test_case in test_cases:
        # Ensure edited is always a boolean, even if it's None in the database
        edited = bool(test_case.edited) if test_case.edited is not None else False

        test_cases_data.append({
            'id': test_case.id,
            'scenario': test_case.scenario,
            'action': test_case.action,
            'expected_behavior': test_case.expected_behavior,
            'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.created_at is not None else '',
            'edited': edited
        })

    return jsonify({"success": True, "test_cases": test_cases_data})

@app.route('/get_tickets')
def get_tickets():
    """Endpoint to get the current list of tickets from the fetch_backlog process status."""
    # Get tickets with their test cases
    tickets_data = []
    from app.db.model import SessionLocal, Ticket, TestCase

    # Only show tickets from the current fetch
    if process_status['fetch_backlog']['tickets']:
        # Get tickets from the current fetch
        jira_keys = [ticket['jira_key'] for ticket in process_status['fetch_backlog']['tickets']]

        # Get details and test cases for these tickets
        session = SessionLocal()
        tickets = session.query(Ticket).filter(Ticket.jira_key.in_(jira_keys)).all()

        for ticket in tickets:
            # Get test cases for this ticket
            test_cases = session.query(TestCase).filter(TestCase.ticket_id == ticket.id).all()

            ticket_data = {
                'jira_key': ticket.jira_key,
                'title': ticket.title,
                'description': ticket.description,
                'issue_type': ticket.issue_type,
                'status': ticket.status,
                'has_test_cases': ticket.test_cases_generated,
                'test_cases': []
            }

            # Add test cases if any
            for test_case in test_cases:
                ticket_data['test_cases'].append({
                    'id': test_case.id,
                    'scenario': test_case.scenario,
                    'action': test_case.action,
                    'expected_behavior': test_case.expected_behavior,
                    'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.created_at is not None else ''
                })

            tickets_data.append(ticket_data)

        session.close()
    else:
        # No tickets in process_status
        pass

    return jsonify(tickets_data)

@app.route('/update_test_case/<test_case_id>', methods=['POST'])
def update_test_case(test_case_id):
    """Endpoint to update a test case with new values."""
    from app.db.model import SessionLocal, TestCase
    from sqlalchemy.orm.exc import DetachedInstanceError
    from sqlalchemy.orm import make_transient_to_detached

    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Get required fields from request
    scenario = data.get('scenario')
    action = data.get('action')
    expected_behavior = data.get('expected_behavior')

    # Validate required fields
    if not all([scenario, action, expected_behavior]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    session = SessionLocal()

    try:
        # Get the test case by ID
        test_case = session.query(TestCase).get(test_case_id)

        if not test_case:
            session.close()
            return jsonify({"success": False, "message": f"Test case {test_case_id} not found"}), 404

        # Update attributes
        test_case.scenario = scenario
        test_case.action = action
        test_case.expected_behavior = expected_behavior
        test_case.edited = True  # Set the edited flag

        # Explicitly merge and commit (using merge instead of add to handle detached instances)
        session.merge(test_case)
        session.commit()
        session.refresh(test_case)  # Refresh to ensure we have the latest data

        # Get the updated data
        updated_test_case = {
            "id": test_case.id,
            "scenario": test_case.scenario,
            "action": test_case.action,
            "expected_behavior": test_case.expected_behavior,
            "edited": test_case.edited
        }

        session.close()

        return jsonify({
            "success": True,
            "message": "Test case updated successfully",
            "test_case": updated_test_case
        })
    except Exception as e:
        import traceback
        print(f"Error updating test case: {str(e)}")
        print(traceback.format_exc())
        session.rollback()
        session.close()
        return jsonify({"success": False, "message": f"Error updating test case: {str(e)}"}), 500

@app.route('/send_to_jira/<ticket_id>', methods=['POST'])
def send_to_jira(ticket_id):
    """Send test cases as a comment to the corresponding Jira ticket."""
    from app.db.model import SessionLocal, Ticket, TestCase
    import requests
    import json
    from datetime import datetime

    app.logger.info(f"Received request to send test cases for ticket {ticket_id} to Jira")
    app.logger.info(f"Request headers: {dict(request.headers)}")
    app.logger.info(f"Request data: {request.get_data(as_text=True)}")

    # Get Jira configuration
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
    JIRA_USER = os.getenv("JIRA_USER", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

    if not JIRA_BASE_URL or not JIRA_USER or not JIRA_API_TOKEN:
        app.logger.error("Missing Jira configuration")
        return jsonify({
            "success": False,
            "message": "Missing Jira configuration. Please set JIRA_BASE_URL, JIRA_USER, and JIRA_API_TOKEN in .env"
        }), 400

    # Get the ticket and its test cases
    session = SessionLocal()
    try:
        ticket = session.query(Ticket).filter(Ticket.jira_key == ticket_id).first()

        if not ticket:
            app.logger.error(f"Ticket {ticket_id} not found")
            session.close()
            return jsonify({"success": False, "message": f"Ticket {ticket_id} not found"}), 404

        app.logger.info(f"Found ticket {ticket_id} in database")
        test_cases = session.query(TestCase).filter(TestCase.ticket_id == ticket.id).all()

        if not test_cases:
            app.logger.error(f"No test cases found for ticket {ticket_id}")
            session.close()
            return jsonify({"success": False, "message": f"No test cases found for ticket {ticket_id}"}), 404

        app.logger.info(f"Found {len(test_cases)} test cases for ticket {ticket_id}")

        # Format test cases as a comment
        comment_body = f"*Test Cases for {ticket_id}*\n\n"
        for i, test_case in enumerate(test_cases, 1):
            edited_mark = " (Edited)" if test_case.edited is True else ""
            comment_body += f"*Test Case {i}{edited_mark}*\n"
            comment_body += f"*Scenario:* {test_case.scenario}\n"
            comment_body += f"*Action:* {test_case.action}\n"
            comment_body += f"*Expected Behavior:* {test_case.expected_behavior}\n\n"

        comment_body += f"\n_Generated by TestCasesGenerator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        app.logger.info(f"Formatted comment body for Jira")

        # Create Jira comment
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
        app.logger.info(f"Sending request to Jira API: {url}")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        auth = (JIRA_USER, JIRA_API_TOKEN)

        # Format as Atlassian Document Format for better formatting in Jira
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment_body
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(url, headers=headers, json=payload, auth=auth)
        app.logger.info(f"Jira API response status: {response.status_code}")

        if response.status_code in [200, 201]:
            app.logger.info(f"Successfully posted test cases to Jira ticket {ticket_id}")
            # Update the ticket in the database
            setattr(ticket, 'posted_to_jira', True)
            session.commit()

            session.close()
            return jsonify({
                "success": True,
                "message": f"Test cases successfully posted to Jira ticket {ticket_id}"
            })
        else:
            app.logger.error(f"Error posting to Jira: {response.status_code} - {response.text}")
            session.close()
            return jsonify({
                "success": False,
                "message": f"Error posting to Jira: {response.status_code} - {response.text}"
            }), 500

    except Exception as e:
        app.logger.exception(f"Error sending test cases to Jira: {str(e)}")
        session.rollback()
        session.close()
        return jsonify({
            "success": False,
            "message": f"Error sending test cases to Jira: {str(e)}"
        }), 500

@app.route('/jira_button/<ticket_id>', methods=['GET'])
def jira_button_action(ticket_id):
    """Alternative endpoint for the Send to Jira button - works without JavaScript."""
    app.logger.info(f"Direct button action for ticket {ticket_id}")

    try:
        # Call the existing send_to_jira function to send to Jira
        response = send_to_jira(ticket_id)

        # Get data from the response
        if isinstance(response, tuple):
            data, status_code = response
        else:
            data = response
            status_code = 200

        # Flash success or error message here if needed
        app.logger.info(f"Jira button action completed with status: {status_code}")

    except Exception as e:
        app.logger.exception(f"Error in jira_button_action: {str(e)}")

    # Always redirect back to the main page with the ticket anchor
    return redirect(url_for('index', _anchor=f"ticket-{ticket_id}"))

@app.route('/diagnostic/test_api', methods=['GET', 'POST'])
def diagnostic_test_api():
    """A simple diagnostic endpoint to test API connectivity."""
    app.logger.info("Diagnostic API test endpoint called")
    
    # Check if Jira environment variables are set
    jira_env_check = {
        "JIRA_BASE_URL": os.getenv("JIRA_BASE_URL", ""),
        "JIRA_USER": os.getenv("JIRA_USER", ""),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", "")
    }
    
    # Mask sensitive info
    masked_env = {
        key: (value[:3] + "..." if value and key != "JIRA_BASE_URL" else value) 
        for key, value in jira_env_check.items()
    }
    
    return jsonify({
        "success": True,
        "message": "Diagnostic API test successful",
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "jira_env_check": masked_env,
        "jira_env_valid": all(jira_env_check.values())
    })

@app.route('/ticket_jira_status/<ticket_id>', methods=['GET'])
def ticket_jira_status(ticket_id):
    """Check if test cases for a specific ticket have already been sent to Jira."""
    from app.db.model import SessionLocal, Ticket
    
    app.logger.info(f"Checking Jira posting status for ticket {ticket_id}")
    
    try:
        session = SessionLocal()
        ticket = session.query(Ticket).filter(Ticket.jira_key == ticket_id).first()
        
        if not ticket:
            app.logger.error(f"Ticket {ticket_id} not found when checking Jira status")
            session.close()
            return jsonify({"success": False, "message": f"Ticket {ticket_id} not found"}), 404
        
        jira_status = {
            "ticket_id": ticket_id,
            "posted_to_jira": bool(ticket.posted_to_jira)
        }
        
        app.logger.info(f"Jira status for ticket {ticket_id}: posted_to_jira={jira_status['posted_to_jira']}")
        session.close()
        return jsonify({"success": True, "data": jira_status})
        
    except Exception as e:
        app.logger.exception(f"Error checking Jira status: {str(e)}")
        return jsonify({"success": False, "message": f"Error checking Jira status: {str(e)}"}), 500

def start():
    """
    Start the Flask application with debug mode enabled.
    This function is called from run_ui.py
    """
    app.run(debug=True)
