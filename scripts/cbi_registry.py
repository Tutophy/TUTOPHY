
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ==========================================
# CBI | CYBER BUREAU OF INTELLIGENCE
# PROJECT INTELLIGENCE ENGINE v1.0
# ==========================================

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "Tutophy")
TOKEN = os.getenv("GITHUB_TOKEN", "")

START_MARKER = "<!-- CBI:AUTO:PROJECTS:START -->"
END_MARKER = "<!-- CBI:AUTO:PROJECTS:END -->"

README = Path(__file__).resolve().parents[1] / "README.md"


def fetch_repositories():
    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        "?sort=updated&per_page=100&type=owner"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CBI-Intelligence-Engine",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def format_projects(repositories):
    projects = []

    for repo in repositories:
        if repo.get("fork") or repo.get("archived"):
            continue

        if repo["name"].lower() == USERNAME.lower():
            continue

        projects.append(repo)

    projects.sort(
        key=lambda item: item.get("updated_at", ""),
        reverse=True
    )

    if not projects:
        return (
            "<div align='center'>"
            "No public projects are currently registered."
            "</div>"
        )

    output = [
        '<table width="100%">',
        '<tr><th>PROJECT</th><th>TECHNOLOGY</th>'
        '<th>LAST UPDATED</th></tr>'
    ]

    for repo in projects[:12]:
        name = repo["name"]
        url = repo["html_url"]
        description = (
            repo.get("description")
            or "Technical research and development."
        )

        description = (
            description.replace("|", "&#124;")
            .replace("\n", " ")
        )

        language = repo.get("language") or "Multiple"

        updated = datetime.strptime(
            repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d")

        output.append(
            f"<tr>"
            f"<td><a href='{url}'><b>{name}</b></a>"
            f"<br/><sub>{description[:120]}</sub></td>"
            f"<td>{language}</td>"
            f"<td>{updated}</td>"
            f"</tr>"
        )

    output.append("</table>")

    return "\n".join(output)


def update_readme(project_content):
    if not README.exists():
        raise FileNotFoundError("README.md was not found.")

    content = README.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("CBI project registry markers are missing.")

    before, remainder = content.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    replacement = (
        f"\n\n"
        f'<div align="center">'
        f'<sub>LAST SYNCHRONIZATION: {timestamp}</sub>'
        f'</div>\n\n'
        f"{project_content}\n\n"
    )

    updated_content = (
        before
        + START_MARKER
        + replacement
        + END_MARKER
        + after
    )

    README.write_text(updated_content, encoding="utf-8")


def main():
    print("======================================")
    print(" CBI PROJECT INTELLIGENCE ENGINE")
    print("======================================")

    print(f"Subject: {USERNAME}")
    print("Connecting to GitHub Intelligence API...")

    repositories = fetch_repositories()

    print(f"Repositories discovered: {len(repositories)}")

    project_content = format_projects(repositories)

    update_readme(project_content)

    print("README successfully synchronized.")
    print("CBI ENGINE: OPERATION COMPLETED")


if __name__ == "__main__":
    main()
