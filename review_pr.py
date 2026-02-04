import os
import requests
from anthropic import Anthropic

# --- Required environment variables ---
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

# Extract PR number safely
GITHUB_REF = os.environ["GITHUB_REF"]
PR_NUMBER = GITHUB_REF.split("/")[-1]

# --- GitHub API headers ---
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# --- Fetch PR metadata ---
pr_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}"
pr_response = requests.get(pr_url, headers=headers)
pr_response.raise_for_status()
pr_data = pr_response.json()

# --- Fetch PR diff ---
diff_response = requests.get(pr_data["diff_url"], headers=headers)
diff_response.raise_for_status()
pr_diff = diff_response.text

# --- Initialize Claude client ---
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# --- Claude prompt ---
prompt = f"""
You are a senior software engineer performing a GitHub pull request review.

Review the following diff and provide:

1. A concise summary
2. Major issues (bugs, correctness, regressions)
3. Minor suggestions (style, clarity, maintainability)
4. Questions for the author (if any)

Be precise, constructive, and actionable.
Do not restate the diff verbatim.

Diff:
{pr_diff}
"""

# --- Call Claude ---
response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1200,
    temperature=0.2,
    messages=[{"role": "user", "content": prompt}],
)

review_text = response.content[0].text

# --- Post comment to PR ---
comments_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues/{PR_NUMBER}/comments"

payload = {
    "body": f"## 🤖 Claude AI Code Review\n\n{review_text}"
}

post_response = requests.post(comments_url, headers=headers, json=payload)
post_response.raise_for_status()

print("Claude review posted successfully.")
