#!/usr/bin/env python3
"""
Custom GitHub stats generator -- orchestrator.
Avoids GitHub's flaky REST /stats/contributors endpoint entirely by using the
stable GraphQL API plus local git operations. See github_api.py, fetch_stats.py,
and render_svg.py for the actual logic.
"""
import os

from fetch_stats import fetch_basic_info, fetch_total_contributions, fetch_total_loc
from render_svg import render_stats_svg, render_langs_svg, render_trophies_svg

info = fetch_basic_info()
total_contributions = fetch_total_contributions(info["created_at"])
total_loc = fetch_total_loc(info["login"], info["repos"])

os.makedirs("assets", exist_ok=True)

stats_svg = render_stats_svg(
    name=info["name"],
    total_stars=info["total_stars"],
    total_forks=info["total_forks"],
    total_contributions=total_contributions,
    total_repos=info["total_repos"],
    followers=info["followers"],
    total_loc=total_loc,
    repos_contributed_to=info["repos_contributed_to"],
)

langs_svg = render_langs_svg(
    top_langs=info["top_langs"],
    total_lang_bytes=info["total_lang_bytes"],
    lang_colors=info["lang_colors"],
)

with open("assets/stats.svg", "w") as f:
    f.write(stats_svg)

with open("assets/languages.svg", "w") as f:
    f.write(langs_svg)

trophies_svg = render_trophies_svg(
    total_stars=info["total_stars"],
    followers=info["followers"],
    total_contributions=total_contributions,
    total_repos=info["total_repos"],
    total_loc=total_loc,
)

with open("assets/trophies.svg", "w") as f:
    f.write(trophies_svg)

print(
    f"Done. Stars={info['total_stars']} Forks={info['total_forks']} "
    f"Contributions={total_contributions} Repos={info['total_repos']} "
    f"Followers={info['followers']} CurrentLOC={total_loc} "
    f"ReposContributedTo={info['repos_contributed_to']}"
)
print(f"Top languages: {info['top_langs']}")
