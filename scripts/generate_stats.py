#!/usr/bin/env python3
"""
Custom GitHub stats generator.
Avoids the flaky REST /stats/contributors endpoint entirely -- uses only the
stable GraphQL API (contributionsCollection, repository languages) which does
not suffer from GitHub's "202 / No Content, still computing" backend issue.
"""
import os
import sys
import datetime
import urllib.request
import json

TOKEN = os.environ.get("ACCESS_TOKEN")
if not TOKEN:
    print("ERROR: ACCESS_TOKEN environment variable not set.", file=sys.stderr)
    sys.exit(1)

API_URL = "https://api.github.com/graphql"

def gql(query, variables=None):
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

# --- Step 1: basic profile info + repo list (single query, no per-repo REST calls) ---
BASIC_QUERY = """
query {
  viewer {
    login
    name
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: [OWNER], isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        name
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""

basic = gql(BASIC_QUERY)["viewer"]
login = basic["login"]
name = basic["name"] or login
created_at = basic["createdAt"]
followers = basic["followers"]["totalCount"]
repos = basic["repositories"]["nodes"]
total_repos = basic["repositories"]["totalCount"]

total_stars = sum(r["stargazerCount"] for r in repos)
total_forks = sum(r["forkCount"] for r in repos)

lang_bytes = {}
lang_colors = {}
for r in repos:
    for edge in r["languages"]["edges"]:
        lname = edge["node"]["name"]
        lang_bytes[lname] = lang_bytes.get(lname, 0) + edge["size"]
        lang_colors[lname] = edge["node"]["color"] or "#888888"

top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:5]
total_lang_bytes = sum(lang_bytes.values()) or 1

# --- Step 2: total contributions, looping per calendar year (GraphQL caps at 1 year per call) ---
CONTRIB_QUERY = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
    }
  }
}
"""

start_year = int(created_at[:4])
current_year = datetime.datetime.utcnow().year
total_contributions = 0

for year in range(start_year, current_year + 1):
    frm = f"{year}-01-01T00:00:00Z"
    to = f"{year}-12-31T23:59:59Z"
    try:
        c = gql(CONTRIB_QUERY, {"from": frm, "to": to})["viewer"]["contributionsCollection"]
        total_contributions += (
            c["totalCommitContributions"]
            + c["totalIssueContributions"]
            + c["totalPullRequestContributions"]
            + c["totalPullRequestReviewContributions"]
            + c["restrictedContributionsCount"]
        )
    except Exception as e:
        print(f"Warning: failed to fetch contributions for {year}: {e}", file=sys.stderr)

# --- Step 3: render SVGs, styled to match the profile's existing palette ---
os.makedirs("assets", exist_ok=True)

STATS_SVG = f'''<svg width="480" height="190" viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="480" height="190" rx="12" fill="#0d0d12" stroke="#9333EA" stroke-opacity="0.3"/>
  <text x="24" y="36" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#EDE3FF" font-weight="bold">{name}'s GitHub Stats</text>
  <line x1="24" y1="48" x2="456" y2="48" stroke="#4ECDC4" stroke-opacity="0.3"/>

  <text x="24" y="80" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">★ Total Stars:</text>
  <text x="456" y="80" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">{total_stars:,}</text>

  <text x="24" y="105" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">⑂ Total Forks:</text>
  <text x="456" y="105" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">{total_forks:,}</text>

  <text x="24" y="130" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">✓ Total Contributions:</text>
  <text x="456" y="130" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">{total_contributions:,}</text>

  <text x="24" y="155" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">◆ Public Repos:</text>
  <text x="456" y="155" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">{total_repos:,}</text>

  <text x="24" y="180" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">◈ Followers:</text>
  <text x="456" y="180" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">{followers:,}</text>
</svg>'''

lang_rows = ""
y_pos = 66
for lname, size in top_langs:
    pct = size / total_lang_bytes * 100
    color = lang_colors.get(lname, "#888888")
    bar_width = 260 * (pct / 100)
    lang_rows += f'''
  <text x="24" y="{y_pos}" font-family="ui-monospace, monospace" font-size="12" fill="#EDE3FF">{lname}</text>
  <text x="456" y="{y_pos}" text-anchor="end" font-family="ui-monospace, monospace" font-size="12" fill="#cfd8e3">{pct:.1f}%</text>
  <rect x="24" y="{y_pos + 6}" width="260" height="6" rx="3" fill="#ffffff" fill-opacity="0.08"/>
  <rect x="24" y="{y_pos + 6}" width="{bar_width:.1f}" height="6" rx="3" fill="{color}"/>'''
    y_pos += 30

LANGS_SVG = f'''<svg width="480" height="{y_pos + 20}" viewBox="0 0 480 {y_pos + 20}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="480" height="{y_pos + 20}" rx="12" fill="#0d0d12" stroke="#9333EA" stroke-opacity="0.3"/>
  <text x="24" y="36" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#EDE3FF" font-weight="bold">Most Used Languages</text>
  <line x1="24" y1="48" x2="456" y2="48" stroke="#4ECDC4" stroke-opacity="0.3"/>
  {lang_rows}
</svg>'''

with open("assets/stats.svg", "w") as f:
    f.write(STATS_SVG)

with open("assets/languages.svg", "w") as f:
    f.write(LANGS_SVG)

print(f"Done. Stars={total_stars} Forks={total_forks} Contributions={total_contributions} Repos={total_repos} Followers={followers}")
print(f"Top languages: {top_langs}")
