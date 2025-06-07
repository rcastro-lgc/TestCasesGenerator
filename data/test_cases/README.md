# Generated Test Cases Directory

This directory contains AI-generated test cases for Jira tickets processed by ProRef.

## File Format

When you run `python scripts/generate_test_cases.py`, it will create a file called `test_cases_by_ticket.md` with the following structure:

```markdown
## TICKET-123 - Implement User Authentication
**Type:** story

**Generated Test Cases:**

### Functional Tests
1. **Valid Login Test**
   - **Given:** User has valid credentials
   - **When:** User enters correct username and password
   - **Then:** User should be successfully authenticated and redirected to dashboard

2. **Invalid Login Test**
   - **Given:** User enters incorrect credentials
   - **When:** User attempts to login
   - **Then:** System should display error message and not authenticate user

### Edge Cases
1. **Empty Fields Test**
   - **Given:** Login form is displayed
   - **When:** User submits form with empty username or password
   - **Then:** System should display validation errors

2. **SQL Injection Test**
   - **Given:** Login form accepts input
   - **When:** User enters SQL injection attempt in username field
   - **Then:** System should sanitize input and not execute malicious code

### Security Tests
1. **Brute Force Protection**
   - **Given:** User has failed login 5 times
   - **When:** User attempts 6th login
   - **Then:** Account should be temporarily locked

---

## TICKET-124 - Fix Email Notification Bug
**Type:** bug

**Generated Test Cases:**

### Regression Tests
1. **Email Delivery Test**
   - **Given:** System needs to send notification email
   - **When:** Notification event is triggered
   - **Then:** Email should be delivered to recipient's inbox

2. **Email Content Test**
   - **Given:** Email notification is sent
   - **When:** Recipient opens email
   - **Then:** Email should contain correct subject and body content
```

## Usage

1. First, fetch your tickets: `python scripts/fetch_backlog.py`
2. Then generate test cases: `python scripts/generate_test_cases.py`
3. The generated test cases will appear in `test_cases_by_ticket.md`

The test cases are designed to help with:
- QA test planning and execution
- Identifying functional and edge case scenarios
- Security and performance testing considerations
- Regression testing after bug fixes 