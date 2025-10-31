import csv
import requests
import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import subprocess

    subprocess.run(["chcp", "65001"], shell=True, capture_output=True)
    sys.stdout.reconfigure(encoding="utf-8")

# ============ CONFIGURATION ============
GITHUB_TOKEN = "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"  # 🔒 Replace with your GitHub Personal Access Token
REPO = "ShadSafa/UseCaseSimulator"  # e.g., "shadisafa/hubro-simulation"
CSV_FILE = "Specs/tasks_kanban.csv"  # The CSV exported from ChatGPT

# 🧩 Project details (get these from your GitHub Project board)
PROJECT_ID = "5"  # From URL: https://github.com/users/ShadSafa/projects/5
COLUMN_IDS = {"To Do": "Backlog", "In Progress": "In progress", "Done": "Done"}

# Label color hex codes (GitHub label colors)
PHASE_COLORS = {
    "Setup": "0366d6",  # Blue
    "Core Modules": "28a745",  # Green
    "User Interface": "f39c12",  # Orange
    "Analytics & Reports": "6f42c1",  # Purple
    "Data Persistence": "20b2aa",  # Teal
    "Scenario Management": "ff69b4",  # Pink
    "Testing & QA": "d73a4a",  # Red
    "Tutorials / Guides": "f4c542",  # Yellow
    "Playtesting / Validation": "808080",  # Gray
}

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


# ============ HELPER FUNCTIONS ============
def github_request(method, url, **kwargs):
    """Simple GitHub API wrapper with error handling"""
    response = requests.request(method, url, headers=HEADERS, **kwargs)
    if not response.ok:
        print(f"❌ GitHub API Error {response.status_code}: {response.text}")
    return response


def ensure_label_exists(label_name, color_hex):
    """Create label if it doesn't exist"""
    url = f"https://api.github.com/repos/{REPO}/labels"
    response = github_request("GET", url)
    labels = [lbl["name"] for lbl in response.json()]

    if label_name not in labels:
        payload = {"name": label_name, "color": color_hex}
        create = github_request("POST", url, json=payload)
        if create.status_code == 201:
            print(f"✅ Created label: {label_name}")
    else:
        print(f"ℹ️ Label exists: {label_name}")


def create_issue(title, body, labels):
    """Create an issue in the repository"""
    url = f"https://api.github.com/repos/{REPO}/issues"
    payload = {"title": title, "body": body, "labels": labels}
    response = github_request("POST", url, json=payload)
    if response.status_code == 201:
        issue_number = response.json()["number"]
        print(f"✅ Created Issue #{issue_number}: {title}")
        return issue_number
    return None


def get_issue_node_id(issue_number):
    """Fetch issue node_id for linking to projects"""
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}"
    response = github_request("GET", url)
    if response.ok:
        return response.json()["node_id"]
    return None


def get_column_id_by_name(column_name):
    """Get column ID by name from the project"""
    url = f"https://api.github.com/projects/{PROJECT_ID}/columns"
    response = github_request("GET", url)
    print(f"Project columns API response status: {response.status_code}")
    if response.status_code == 404:
        print(
            "❌ Project not found or not accessible. This might be a new GitHub Projects (beta) project."
        )
        print(
            "💡 For new Projects, issues are added automatically when linked, not via API."
        )
        return None
    if response.ok:
        columns = response.json()
        print(f"Found {len(columns)} columns in project")
        for column in columns:
            print(f"Column: {column['name']} (ID: {column['id']})")
            if column["name"] == column_name:
                return column["id"]
    else:
        print(f"❌ Failed to get project columns: {response.text}")
    return None


def add_issue_to_project(issue_number, column_name):
    """Add issue card to GitHub Project Kanban column"""
    # Skip project integration for new GitHub Projects (beta)
    print(
        f"ℹ️ Skipping project integration for Issue #{issue_number} - using new Projects API"
    )
    return


# ============ MAIN SCRIPT ============
def main():
    print("\n🚀 Starting GitHub Kanban Import...\n")

    # Ensure all phase labels exist
    for phase, color in PHASE_COLORS.items():
        ensure_label_exists(phase, color)

    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = f"{row['Task_ID']} - {row['Title']}"
            description = (
                f"{row['Description']}\n\n**Dependencies:** {row['Dependencies']}"
            )
            phase = row["Phase"]
            status = row["Status"]

            # Get label color for phase
            ensure_label_exists(phase, PHASE_COLORS.get(phase, "ededed"))
            labels = [phase]

            # Pick Kanban column
            column_name = COLUMN_IDS.get(status, COLUMN_IDS["To Do"])

            issue_number = create_issue(title, description, labels)
            if issue_number:
                add_issue_to_project(issue_number, column_name)

    print("\n✅ Import complete! Check your GitHub Project board.\n")


if __name__ == "__main__":
    main()
