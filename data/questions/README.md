# Generated Questions Directory

This directory contains AI-generated questions for Jira tickets processed by ProRef.

## File Format

When you run `python scripts/generate_questions.py`, it will create a file called `questions_by_ticket.md` with the following structure:

```markdown
## TICKET-123 - Implement User Authentication
**Type:** story

**Generated questions:**
- What authentication methods should be supported (password, OAuth, SSO)?
- How should failed login attempts be handled and logged?
- What are the password complexity requirements?
- How should user sessions be managed and expired?
- What security measures should be implemented to prevent brute force attacks?

---

## TICKET-124 - Fix Email Notification Bug
**Type:** bug

**Generated questions:**
- What specific conditions cause the email notifications to fail?
- Are there any error logs or patterns that can help identify the root cause?
- How should the system handle email delivery failures?
- What testing strategy should be used to verify the fix?
- Are there any dependencies on external email services that need to be considered?
```

## Usage

1. First, fetch your tickets: `python scripts/fetch_backlog.py`
2. Then generate questions: `python scripts/generate_questions.py`
3. The generated questions will appear in `questions_by_ticket.md`

The questions are designed to help with:
- Sprint planning and refinement
- Identifying edge cases and requirements
- QA test planning
- Technical implementation considerations 