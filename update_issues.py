import requests
import json

# GitHub API details
GITHUB_TOKEN = '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'
REPO_OWNER = 'ShadSafa'
REPO_NAME = 'UseCaseSimulator'
PROJECT_NUMBER = 5  # From the URL: https://github.com/users/ShadSafa/projects/5

# GraphQL endpoint
GRAPHQL_URL = 'https://api.github.com/graphql'
HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json'
}

# List of completed tasks
completed_tasks = [
    "Setup Python Project",
    "Create Project Folder Structure",
    "Setup Git Repository",
    "Setup Python Linter and Formatter",
    "Install Required Libraries",
    "Design Simulation Engine Architecture",
    "Implement Base Simulation Engine",
    "Define Simulation Round Logic",
    "Create Company Class",
    "Implement Company Financial Methods",
    "Define Decision-Making Methods",
    "Create Market Class",
    "Implement Market Demand Simulation",
    "Implement Competitor AI",
    "Design Event System",
    "Implement Random Events",
    "Implement Scheduled Events",
    "Implement Multi-Round Simulation",
    "Create UI Module",
    "Implement Decision Input Forms",
    "Implement Dashboard Output",
    "Implement End-of-Round Summary",
    "Implement Player Notifications",
    "Implement User Settings"
]

# Function to execute GraphQL query
def graphql_query(query, variables=None):
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
            return None
        return data['data']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Function to get issues
def get_issues():
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        issues(first: 100, states: OPEN) {
          nodes {
            number
            title
            id
          }
        }
      }
    }
    """
    variables = {'owner': REPO_OWNER, 'name': REPO_NAME}
    data = graphql_query(query, variables)
    if data:
        return data['repository']['issues']['nodes']
    return []

# Function to get project ID
def get_project_id():
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """
    variables = {'owner': REPO_OWNER, 'name': REPO_NAME, 'number': PROJECT_NUMBER}
    data = graphql_query(query, variables)
    if data and data['repository']['projectV2']:
        return data['repository']['projectV2']['id']
    return None

# Function to add issue to project
def add_issue_to_project(project_id, issue_id):
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    variables = {'projectId': project_id, 'contentId': issue_id}
    data = graphql_query(mutation, variables)
    if data:
        print(f"Added issue to project")
        return data['addProjectV2ItemById']['item']['id']
    return None

# Function to set issue status in project
def set_issue_status(project_id, item_id, status_value):
    # First, get the field ID for status
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    data = graphql_query(query, {'projectId': project_id})
    if not data:
        return False
    status_field = None
    status_option_id = None
    for field in data['node']['fields']['nodes']:
        if field['name'] == 'Status':
            status_field = field
            for option in field['options']:
                if option['name'] == status_value:
                    status_option_id = option['id']
                    break
            break
    if not status_field or not status_option_id:
        print("Status field or 'Done' option not found")
        return False

    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: {singleSelectOptionId: $value}
      }) {
        projectV2Item {
          id
        }
      }
    }
    """
    variables = {
        'projectId': project_id,
        'itemId': item_id,
        'fieldId': status_field['id'],
        'value': status_option_id
    }
    data = graphql_query(mutation, variables)
    if data:
        print(f"Set issue status to {status_value}")
        return True
    return False

# Main function
def main():
    project_id = get_project_id()
    if not project_id:
        print("Could not find project")
        return

    issues = get_issues()
    for issue in issues:
        if issue['title'] in completed_tasks:
            # Check if issue is already in project
            # For simplicity, assume we add it if not present; in real scenario, query project items
            item_id = add_issue_to_project(project_id, issue['id'])
            if item_id:
                set_issue_status(project_id, item_id, 'Done')

if __name__ == "__main__":
    main()