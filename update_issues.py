import requests
import csv

# GitHub API details
GITHUB_TOKEN = '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'
REPO_OWNER = 'shadisafa'
REPO_NAME = 'usecasesimulator'

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

# Function to get issues
def get_issues():
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching issues: {response.status_code} - {response.text}")
        return []

# Function to update issue status
def update_issue(issue_number, status):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {'state': status}
    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Updated issue #{issue_number} to {status}")
    else:
        print(f"Error updating issue #{issue_number}: {response.status_code} - {response.text}")

# Main function
def main():
    issues = get_issues()
    for issue in issues:
        if issue['title'] in completed_tasks:
            update_issue(issue['number'], 'closed')

if __name__ == "__main__":
    main()