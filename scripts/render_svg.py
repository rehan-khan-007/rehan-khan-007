"""Renders the two stat SVGs from already-fetched data."""


def render_stats_svg(name, total_stars, total_forks, total_contributions,
                      total_repos, followers, total_loc, repos_contributed_to):
    name_escaped = name.replace("'", "&#39;")

    return """<svg width="480" height="280" viewBox="0 0 480 280" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="480" height="280" rx="12" fill="#0d0d12" stroke="#9333EA" stroke-opacity="0.3"/>
  <text x="24" y="36" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#EDE3FF" font-weight="bold">""" + name_escaped + """&#39;s GitHub Stats</text>
  <line x1="24" y1="48" x2="456" y2="48" stroke="#4ECDC4" stroke-opacity="0.3"/>

  <text x="24" y="80" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Total Stars:</text>
  <text x="456" y="80" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{total_stars:,}" + """</text>

  <text x="24" y="105" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Total Forks:</text>
  <text x="456" y="105" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{total_forks:,}" + """</text>

  <text x="24" y="130" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Total Contributions:</text>
  <text x="456" y="130" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{total_contributions:,}" + """</text>

  <text x="24" y="155" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Public Repos:</text>
  <text x="456" y="155" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{total_repos:,}" + """</text>

  <text x="24" y="180" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Followers:</text>
  <text x="456" y="180" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{followers:,}" + """</text>

  <text x="24" y="205" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Current Lines of Code:</text>
  <text x="456" y="205" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{total_loc:,}" + """</text>

  <text x="24" y="230" font-family="ui-monospace, monospace" font-size="13" fill="#4ECDC4">Repos Contributed To:</text>
  <text x="456" y="230" text-anchor="end" font-family="ui-monospace, monospace" font-size="13" fill="#ffffff">""" + f"{repos_contributed_to:,}" + """</text>
</svg>"""


def render_langs_svg(top_langs, total_lang_bytes, lang_colors):
    lang_rows = ""
    y_pos = 66
    for lname, size in top_langs:
        pct = size / total_lang_bytes * 100
        color = lang_colors.get(lname, "#888888")
        bar_width = 260 * (pct / 100)
        lang_rows += """
  <text x="24" y=\"""" + str(y_pos) + """\" font-family="ui-monospace, monospace" font-size="12" fill="#EDE3FF">""" + lname + """</text>
  <text x="456" y=\"""" + str(y_pos) + """\" text-anchor="end" font-family="ui-monospace, monospace" font-size="12" fill="#cfd8e3">""" + f"{pct:.1f}%" + """</text>
  <rect x="24" y=\"""" + str(y_pos + 6) + """\" width="260" height="6" rx="3" fill="#ffffff" fill-opacity="0.08"/>
  <rect x="24" y=\"""" + str(y_pos + 6) + """\" width=\"""" + f"{bar_width:.1f}" + """\" height="6" rx="3" fill=\"""" + color + """\"/>"""
        y_pos += 30

    return """<svg width="480" height=\"""" + str(y_pos + 20) + """\" viewBox="0 0 480 """ + str(y_pos + 20) + """" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="480" height=\"""" + str(y_pos + 20) + """\" rx="12" fill="#0d0d12" stroke="#9333EA" stroke-opacity="0.3"/>
  <text x="24" y="36" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16" fill="#EDE3FF" font-weight="bold">Most Used Languages</text>
  <line x1="24" y1="48" x2="456" y2="48" stroke="#4ECDC4" stroke-opacity="0.3"/>""" + lang_rows + """
</svg>"""


def _rank_for(value, thresholds):
    """thresholds is a list of (min_value, rank_label, color) tuples, checked
    from highest to lowest. Returns the first one the value qualifies for."""
    for min_value, rank_label, color in thresholds:
        if value >= min_value:
            return rank_label, color
    return "C", "#6b7280"


STAR_THRESHOLDS = [
    (1000, "SSS", "#FFD700"), (500, "SS", "#FFD700"), (100, "S", "#FFD700"),
    (50, "AAA", "#9333EA"), (20, "AA", "#9333EA"), (10, "A", "#9333EA"),
    (3, "B", "#4ECDC4"), (0, "C", "#6b7280"),
]
FOLLOWER_THRESHOLDS = [
    (1000, "SSS", "#FFD700"), (500, "SS", "#FFD700"), (100, "S", "#FFD700"),
    (50, "AAA", "#9333EA"), (25, "AA", "#9333EA"), (10, "A", "#9333EA"),
    (3, "B", "#4ECDC4"), (0, "C", "#6b7280"),
]
CONTRIB_THRESHOLDS = [
    (20000, "SSS", "#FFD700"), (10000, "SS", "#FFD700"), (5000, "S", "#FFD700"),
    (2000, "AAA", "#9333EA"), (1000, "AA", "#9333EA"), (500, "A", "#9333EA"),
    (100, "B", "#4ECDC4"), (0, "C", "#6b7280"),
]
REPO_THRESHOLDS = [
    (50, "SSS", "#FFD700"), (30, "SS", "#FFD700"), (20, "S", "#FFD700"),
    (15, "AAA", "#9333EA"), (10, "AA", "#9333EA"), (5, "A", "#9333EA"),
    (2, "B", "#4ECDC4"), (0, "C", "#6b7280"),
]
LOC_THRESHOLDS = [
    (200000, "SSS", "#FFD700"), (100000, "SS", "#FFD700"), (50000, "S", "#FFD700"),
    (20000, "AAA", "#9333EA"), (10000, "AA", "#9333EA"), (5000, "A", "#9333EA"),
    (1000, "B", "#4ECDC4"), (0, "C", "#6b7280"),
]


def render_trophies_svg(total_stars, followers, total_contributions, total_repos, total_loc):
    trophies = [
        ("Stars", total_stars, STAR_THRESHOLDS),
        ("Followers", followers, FOLLOWER_THRESHOLDS),
        ("Contributions", total_contributions, CONTRIB_THRESHOLDS),
        ("Repos", total_repos, REPO_THRESHOLDS),
        ("Lines of Code", total_loc, LOC_THRESHOLDS),
    ]

    card_width = 140
    card_height = 130
    gap = 12
    total_width = len(trophies) * card_width + (len(trophies) - 1) * gap + 24

    cards = ""
    for i, (label, value, thresholds) in enumerate(trophies):
        rank, color = _rank_for(value, thresholds)
        x = 12 + i * (card_width + gap)
        cards += """
  <g transform="translate(""" + str(x) + """, 12)">
    <rect x="0" y="0" width=\"""" + str(card_width) + """\" height=\"""" + str(card_height) + """\" rx="10" fill="#0d0d12" stroke=\"""" + color + """\" stroke-opacity="0.6" stroke-width="1.5"/>
    <text x=\"""" + str(card_width // 2) + """\" y="30" text-anchor="middle" font-family="ui-monospace, monospace" font-size="11" fill="#cfd8e3">""" + label + """</text>
    <text x=\"""" + str(card_width // 2) + """\" y="78" text-anchor="middle" font-family="ui-monospace, monospace" font-size="36" font-weight="bold" fill=\"""" + color + """\">""" + rank + """</text>
    <text x=\"""" + str(card_width // 2) + """\" y="110" text-anchor="middle" font-family="ui-monospace, monospace" font-size="11" fill="#ffffff">""" + f"{value:,}" + """</text>
  </g>"""

    return """<svg width=\"""" + str(total_width) + """\" height="154" viewBox="0 0 """ + str(total_width) + """ 154" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width=\"""" + str(total_width) + """\" height="154" rx="12" fill="#0d0d12"/>""" + cards + """
</svg>"""
