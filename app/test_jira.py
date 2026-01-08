import os
from dotenv import load_dotenv
from atlassian import Jira

load_dotenv()

jira = Jira(
    url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_EMAIL"),
    password=os.getenv("JIRA_API_TOKEN"),
    cloud=True
)

def create_first_incident():
    project_key = os.getenv("JIRA_PROJECT_KEY")
    # Using the exact name discovered in your metadata
    issue_type_name = 'Report an incident' 
    
    print(f"🛰️ Sentinel: Logging first incident to {project_key}...")
    
    try:
        issue_fields = {
            'project': {'key': project_key},
            'summary': 'SENTINEL: AI Hallucination Detected',
            'description': 'The Logic Auditor has flagged an inconsistency in the primary model output.',
            'issuetype': {'name': issue_type_name}
        }
        
        new_issue = jira.issue_create(fields=issue_fields)
        print(f"🎫 SUCCESS! Incident Created: {new_issue['key']}")
        print(f"🔗 View your incident: {os.getenv('JIRA_URL')}/browse/{new_issue['key']}")

    except Exception as e:
        print(f"❌ Handshake failed: {e}")

if __name__ == "__main__":
    create_first_incident()