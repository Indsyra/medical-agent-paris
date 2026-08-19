"""
GitHub Projects automation script.
Syncs issues to the correct column in GitHub Projects board based on their state.

Usage:
    python sync_github_projects.py

Requirements:
    pip install requests python-dotenv

Environment variables (.env):
    GITHUB_TOKEN=your_github_personal_access_token
    GITHUB_OWNER=Indsyra
    GITHUB_REPO=medical-agent-paris
    GITHUB_PROJECT_NUMBER=1
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "Indsyra")
GITHUB_REPO = os.getenv("GITHUB_REPO", "medical-agent-paris")
GITHUB_PROJECT_NUMBER = int(os.getenv("GITHUB_PROJECT_NUMBER", "1"))

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}


def run_query(query: str, variables: dict = {}) -> dict:
    """Run a GitHub GraphQL query."""
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()


def get_project_id() -> str:
    """Get the project node ID from the project number."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
            projectV2(number: $number) {
                id
                title
            }
        }
    }
    """
    result = run_query(query, {
        "owner": GITHUB_OWNER,
        "repo": GITHUB_REPO,
        "number": GITHUB_PROJECT_NUMBER
    })
    project = result["data"]["repository"]["projectV2"]
    print(f"Project found: {project['title']} (id: {project['id']})")
    return project["id"]


def get_project_fields(project_id: str) -> dict:
    """Get all fields and their options from the project."""
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
    result = run_query(query, {"projectId": project_id})
    fields = result["data"]["node"]["fields"]["nodes"]

    status_field = None
    for field in fields:
        if field and field.get("name") == "Status":
            status_field = field
            break

    if not status_field:
        raise ValueError("Status field not found in project.")

    options = {opt["name"]: opt["id"] for opt in status_field["options"]}
    print(f"Status field found with options: {list(options.keys())}")
    return {"field_id": status_field["id"], "options": options}


def get_repo_issues() -> list:
    """Get all issues from the repository."""
    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            issues(first: 50, states: [OPEN, CLOSED]) {
                nodes {
                    id
                    number
                    title
                    state
                    labels(first: 5) {
                        nodes {
                            name
                        }
                    }
                }
            }
        }
    }
    """
    result = run_query(query, {
        "owner": GITHUB_OWNER,
        "repo": GITHUB_REPO
    })
    issues = result["data"]["repository"]["issues"]["nodes"]
    print(f"Found {len(issues)} issues in repository")
    return issues


def add_issue_to_project(project_id: str, issue_id: str) -> str:
    """Add an issue to the project and return the item ID."""
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {
            projectId: $projectId
            contentId: $contentId
        }) {
            item {
                id
            }
        }
    }
    """
    result = run_query(mutation, {
        "projectId": project_id,
        "contentId": issue_id
    })
    return result["data"]["addProjectV2ItemById"]["item"]["id"]


def get_project_items(project_id: str) -> list:
    """Get all items in the project with their issue state."""
    query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                items(first: 50) {
                    nodes {
                        id
                        fieldValues(first: 10) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    name
                                    field {
                                        ... on ProjectV2SingleSelectField {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                        content {
                            ... on Issue {
                                id
                                number
                                title
                                state
                                labels(first: 5) {
                                    nodes {
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    result = run_query(query, {"projectId": project_id})
    items = result["data"]["node"]["items"]["nodes"]
    print(f"Found {len(items)} items in project")
    return items


def update_item_status(project_id: str, item_id: str, field_id: str, option_id: str) -> None:
    """Update the status of a project item."""
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
        updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $optionId }
        }) {
            projectV2Item {
                id
            }
        }
    }
    """
    run_query(mutation, {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "optionId": option_id
    })


def get_target_column(issue: dict, options: dict) -> str:
    """Determine the target column for an issue based on its state and labels."""
    labels = [label["name"] for label in issue.get("labels", {}).get("nodes", [])]

    if "blocked" in labels and "Blocked" in options:
        return "Blocked"
    if issue["state"] == "CLOSED":
        return "Done"
    if "in progress" in labels and "In Progress" in options:
        return "In Progress"
    return "Todo"


def sync_project() -> None:
    """Main function to sync all issues to the correct column."""
    print("Starting GitHub Projects sync...")

    # Get project info
    project_id = get_project_id()
    fields = get_project_fields(project_id)
    field_id = fields["field_id"]
    options = fields["options"]

    # Get existing items in project
    items = get_project_items(project_id)

    # Track existing issue numbers
    existing_issue_numbers = set()
    for item in items:
        content = item.get("content")
        if content and "number" in content:
            existing_issue_numbers.add(content["number"])

    # Add missing issues to project
    repo_issues = get_repo_issues()
    for issue in repo_issues:
        if issue["number"] not in existing_issue_numbers:
            print(f"  ➕ Adding issue #{issue['number']} '{issue['title']}' to project")
            add_issue_to_project(project_id, issue["id"])

    # Refresh items after adding
    items = get_project_items(project_id)

    # Sync each item to the correct column
    synced = 0
    for item in items:
        content = item.get("content")
        if not content or "number" not in content:
            continue

        issue_number = content["number"]
        issue_title = content["title"]
        target_column = get_target_column(content, options)

        if target_column not in options:
            print(f"  ⚠️  Column '{target_column}' not found for issue #{issue_number} — skipping")
            continue

        option_id = options[target_column]
        update_item_status(project_id, item["id"], field_id, option_id)
        print(f"  ✅ Issue #{issue_number} '{issue_title}' → {target_column}")
        synced += 1

    print(f"\nSync complete: {synced}/{len(items)} issues updated.")


if __name__ == "__main__":
    sync_project()
