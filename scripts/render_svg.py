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
