"""GitHub GraphQL API client -- shared by the other stats modules."""
import os
import sys
import json
import urllib.request

TOKEN = os.environ.get("ACCESS_TOKEN")
if not TOKEN:
    print("ERROR: ACCESS_TOKEN environment variable not set.", file=sys.stderr)
    sys.exit(1)

API_URL = "https://api.github.com/graphql"


def gql(query, variables=None):
    """Run a GraphQL query against the GitHub API and return the 'data' field."""
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "custom-stats-script",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]
