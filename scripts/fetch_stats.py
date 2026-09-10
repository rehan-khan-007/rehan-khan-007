"""Fetches all raw stats data: profile info, contributions, current lines of code."""
import sys
import os
import datetime
import subprocess
import tempfile

from github_api import gql, TOKEN

BASIC_QUERY = """
query {
  viewer {
    login
    name
    createdAt
    followers { totalCount }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
      totalCount
    }
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

CONTRIB_QUERY = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      restrictedContributionsCount
    }
  }
}
"""

# Excludes common generated/dependency artifacts so lockfiles don't dominate the count.
EXCLUDED_PATTERNS = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Cargo.lock", ".min.js", ".min.css", ".svg", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".lock",
)


def fetch_basic_info():
    """Fetch login, name, followers, repo list, stars/forks, and language byte counts."""
    basic = gql(BASIC_QUERY)["viewer"]

    lang_bytes = {}
    lang_colors = {}
    for r in basic["repositories"]["nodes"]:
        for edge in r["languages"]["edges"]:
            lname = edge["node"]["name"]
            lang_bytes[lname] = lang_bytes.get(lname, 0) + edge["size"]
            lang_colors[lname] = edge["node"]["color"] or "#888888"

    top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:5]
    total_lang_bytes = sum(lang_bytes.values()) or 1

    return {
        "login": basic["login"],
        "name": basic["name"] or basic["login"],
        "created_at": basic["createdAt"],
        "followers": basic["followers"]["totalCount"],
        "repos": basic["repositories"]["nodes"],
        "total_repos": basic["repositories"]["totalCount"],
        "repos_contributed_to": basic["repositoriesContributedTo"]["totalCount"],
        "total_stars": sum(r["stargazerCount"] for r in basic["repositories"]["nodes"]),
        "total_forks": sum(r["forkCount"] for r in basic["repositories"]["nodes"]),
        "top_langs": top_langs,
        "lang_colors": lang_colors,
        "total_lang_bytes": total_lang_bytes,
    }


def fetch_total_contributions(created_at):
    """Sum contributions across every calendar year since account creation."""
    start_year = int(created_at[:4])
    current_year = datetime.datetime.utcnow().year
    total = 0

    for year in range(start_year, current_year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        try:
            c = gql(CONTRIB_QUERY, {"from": frm, "to": to})["viewer"]["contributionsCollection"]
            total += (
                c["totalCommitContributions"]
                + c["totalIssueContributions"]
                + c["totalPullRequestContributions"]
                + c["totalPullRequestReviewContributions"]
                + c["totalRepositoryContributions"]
                + c["restrictedContributionsCount"]
            )
        except Exception as e:
            print(f"Warning: failed to fetch contributions for {year}: {e}", file=sys.stderr)

    return total


def _get_current_lines_of_code(owner, repo_name, token):
    """Shallow-clone a repo and count lines in its currently tracked files."""
    with tempfile.TemporaryDirectory() as tmp:
        clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"
        try:
            subprocess.run(
                ["git", "clone", "--quiet", "--depth", "1", clone_url, tmp],
                check=True, timeout=60,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            result = subprocess.run(
                ["git", "-C", tmp, "ls-files"],
                check=True, timeout=30, capture_output=True, text=True,
            )
            total_lines = 0
            for filename in result.stdout.splitlines():
                if any(filename.endswith(p) or p in filename for p in EXCLUDED_PATTERNS):
                    continue
                filepath = os.path.join(tmp, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        total_lines += sum(1 for _ in f)
                except (OSError, IsADirectoryError):
                    continue
            return total_lines
        except Exception as e:
            print(f"Warning: could not count lines for {repo_name}: {e}", file=sys.stderr)
            return 0


def fetch_total_loc(login, repos):
    """Sum current lines of code across all given repos."""
    total = 0
    for r in repos:
        total += _get_current_lines_of_code(login, r["name"], TOKEN)
    return total


CONTRIB_QUERY_WITH_CALENDAR = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      restrictedContributionsCount
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_contributions_and_streaks(created_at):
    start_year = int(created_at[:4])
    current_year = datetime.datetime.utcnow().year
    total = 0
    all_days = []

    for year in range(start_year, current_year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        try:
            c = gql(CONTRIB_QUERY_WITH_CALENDAR, {"from": frm, "to": to})["viewer"]["contributionsCollection"]
            total += (
                c["totalCommitContributions"]
                + c["totalIssueContributions"]
                + c["totalPullRequestContributions"]
                + c["totalPullRequestReviewContributions"]
                + c["totalRepositoryContributions"]
                + c["restrictedContributionsCount"]
            )
            for week in c["contributionCalendar"]["weeks"]:
                for day in week["contributionDays"]:
                    all_days.append((day["date"], day["contributionCount"]))
        except Exception as e:
            print(f"Warning: failed to fetch contributions for {year}: {e}", file=sys.stderr)

    all_days.sort(key=lambda d: d[0])

    longest_streak = 0
    longest_start = longest_end = None
    run_length = 0
    run_start = None
    prev_date = None

    for date_str, count in all_days:
        d = datetime.date.fromisoformat(date_str)
        if count > 0:
            if prev_date is not None and (d - prev_date).days == 1:
                run_length += 1
            else:
                run_length = 1
                run_start = d
            if run_length > longest_streak:
                longest_streak = run_length
                longest_start = run_start
                longest_end = d
            prev_date = d
        else:
            prev_date = None
            run_length = 0

    current_streak = 0
    current_start = current_end = None

    if all_days:
        day_map = {datetime.date.fromisoformat(ds): cnt for ds, cnt in all_days}
        today = max(day_map.keys())
        anchor = today if day_map.get(today, 0) > 0 else today - datetime.timedelta(days=1)

        d = anchor
        streak_days = []
        while day_map.get(d, 0) > 0:
            streak_days.append(d)
            d -= datetime.timedelta(days=1)

        if streak_days:
            current_streak = len(streak_days)
            current_end = streak_days[0]
            current_start = streak_days[-1]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "current_streak_start": current_start,
        "current_streak_end": current_end,
        "longest_streak": longest_streak,
        "longest_streak_start": longest_start,
        "longest_streak_end": longest_end,
    }
