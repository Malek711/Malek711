from __future__ import annotations
import html, json, os, urllib.request
from pathlib import Path

login = os.environ["GITHUB_REPOSITORY_OWNER"]
token = os.environ["GITHUB_TOKEN"]
output = Path(os.environ.get("OUTPUT_PATH", "/tmp/github-contribution-grid-car.svg"))
query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date weekday}}}}}}"""
body = json.dumps({"query": query, "variables": {"login": login}}).encode()
request = urllib.request.Request(
    "https://api.github.com/graphql", data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "Malek711-contribution-car"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    result = json.load(response)
if result.get("errors"):
    raise RuntimeError(result["errors"])

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks, total = calendar["weeks"], calendar["totalContributions"]
cell, step, left, top = 11, 15, 46, 78
width, height = left + len(weeks) * step + 42, top + 7 * step + 70
counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
peak = max(counts, default=1) or 1
colors = ["#EEF2FF", "#CFFAFE", "#A5F3FC", "#7DD3FC", "#6366F1"]

def level(count: int) -> int:
    if count == 0: return 0
    ratio = count / peak
    if ratio <= .18: return 1
    if ratio <= .38: return 2
    if ratio <= .68: return 3
    return 4

cells, points = [], []
for wi, week in enumerate(weeks):
    days = week["contributionDays"]
    for day in (days if wi % 2 == 0 else reversed(days)):
        points.append((left + wi * step + cell / 2, top + day["weekday"] * step + cell / 2))
    for day in days:
        x, y, count = left + wi * step, top + day["weekday"] * step, day["contributionCount"]
        cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{colors[level(count)]}"><title>{html.escape(day["date"])}: {count} contributions</title></rect>')

route = " ".join((f"M {x:.1f} {y:.1f}" if i == 0 else f"L {x:.1f} {y:.1f}") for i, (x, y) in enumerate(points))
safe_login = html.escape(login)
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{safe_login} contribution drive</title><desc id="desc">An animated car travels across {safe_login}'s GitHub contribution days.</desc>
<defs><linearGradient id="header"><stop stop-color="#06B6D4"/><stop offset=".55" stop-color="#6366F1"/><stop offset="1" stop-color="#EC4899"/></linearGradient><filter id="shadow" x="-80%" y="-120%" width="260%" height="340%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#64748B" flood-opacity=".32"/></filter></defs>
<rect width="{width}" height="{height}" rx="22" fill="#FFFFFF"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="21" fill="none" stroke="#E2E8F0"/>
<rect x="22" y="22" width="5" height="31" rx="2.5" fill="url(#header)"/><text x="40" y="38" fill="#0F172A" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="1.8">CONTRIBUTION DRIVE</text><text x="40" y="55" fill="#64748B" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11">{total} contributions in the last year</text>
<g>{''.join(cells)}</g><path id="route" d="{route}" fill="none" stroke="#6366F1" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 7" opacity=".18"/>
<g filter="url(#shadow)"><animateMotion dur="22s" repeatCount="indefinite" rotate="auto"><mpath href="#route"/></animateMotion><path d="M-11,-2 L-7,-8 H4 L9,-3 H11 V4 H-11 V-2 Z" fill="#F43F5E"/><path d="M-5,-7 H3 L6,-3 H-7 Z" fill="#E0F2FE"/><rect x="-12" y="1" width="24" height="4" rx="2" fill="#FB7185"/><circle cx="-7" cy="5" r="3" fill="#334155"/><circle cx="7" cy="5" r="3" fill="#334155"/><circle cx="-7" cy="5" r="1.2" fill="#CBD5E1"/><circle cx="7" cy="5" r="1.2" fill="#CBD5E1"/></g>
<g font-family="Inter,Segoe UI,Arial,sans-serif" font-size="10" fill="#64748B"><text x="{left}" y="{height-25}">Less</text>{''.join(f'<rect x="{left+31+i*16}" y="{height-35}" width="11" height="11" rx="3" fill="{color}"/>' for i,color in enumerate(colors))}<text x="{left+113}" y="{height-25}">More</text></g>
</svg>"""
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(svg, encoding="utf-8")
