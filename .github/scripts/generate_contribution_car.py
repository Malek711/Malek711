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
cell, step, left, top = 10, 14, 44, 66
width, height = left + len(weeks) * step + 38, top + 7 * step + 46
counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
peak = max(counts, default=1) or 1
colors = ["#161B2B", "#0E4F5C", "#0E7490", "#2563EB", "#8B5CF6"]

def level(count: int) -> int:
    if count == 0: return 0
    ratio = count / peak
    if ratio <= .18: return 1
    if ratio <= .38: return 2
    if ratio <= .68: return 3
    return 4

cells = []
for wi, week in enumerate(weeks):
    days = week["contributionDays"]
    for day in days:
        x, y, count = left + wi * step, top + day["weekday"] * step, day["contributionCount"]
        cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{colors[level(count)]}"><title>{html.escape(day["date"])}: {count} contributions</title></rect>')

start_x = left - 18
end_x = left + (len(weeks) - 1) * step + cell + 18
car_y = top + 3 * step + cell / 2
route = f"M {left} {car_y:.1f} H {left + (len(weeks) - 1) * step + cell}"
safe_login = html.escape(login)
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{safe_login} contribution drive</title><desc id="desc">An animated car travels across {safe_login}'s GitHub contribution days.</desc>
<defs><linearGradient id="header"><stop stop-color="#22D3EE"/><stop offset=".55" stop-color="#8B5CF6"/><stop offset="1" stop-color="#F97316"/></linearGradient><filter id="shadow" x="-80%" y="-120%" width="260%" height="340%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#64748B" flood-opacity=".32"/></filter></defs>
<rect width="{width}" height="{height}" rx="22" fill="#0B1220"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="21" fill="none" stroke="#243047"/>
<rect x="22" y="22" width="5" height="31" rx="2.5" fill="url(#header)"/><text x="40" y="38" fill="#F8FAFC" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="1.8">CONTRIBUTION DRIVE</text><text x="40" y="55" fill="#94A3B8" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11">{total} contributions in the last year</text>
<g>{''.join(cells)}</g><path d="{route}" fill="none" stroke="#22D3EE" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="2 7" opacity=".3"/>
<g filter="url(#shadow)"><animateTransform attributeName="transform" type="translate" from="{start_x:.1f} {car_y:.1f}" to="{end_x:.1f} {car_y:.1f}" dur="36s" repeatCount="indefinite"/><path d="M-28,0H-17" stroke="#22D3EE" stroke-width="2" stroke-linecap="round" opacity=".75"><animate attributeName="opacity" values=".2;1;.2" dur=".8s" repeatCount="indefinite"/></path><path d="M-24,-5H-15" stroke="#8B5CF6" stroke-width="1.5" stroke-linecap="round" opacity=".6"/><path d="M-11,-2 L-7,-8 H4 L9,-3 H11 V4 H-11 V-2 Z" fill="#F97316"/><path d="M-5,-7 H3 L6,-3 H-7 Z" fill="#CFFAFE"/><rect x="-12" y="1" width="24" height="4" rx="2" fill="#FB923C"/><circle cx="13" cy="0" r="2.5" fill="#FDE68A"><animate attributeName="opacity" values=".5;1;.5" dur="1s" repeatCount="indefinite"/></circle><circle cx="-7" cy="5" r="3" fill="#0F172A"/><circle cx="7" cy="5" r="3" fill="#0F172A"/><circle cx="-7" cy="5" r="1.2" fill="#CBD5E1"/><circle cx="7" cy="5" r="1.2" fill="#CBD5E1"/></g>
<g font-family="Inter,Segoe UI,Arial,sans-serif" font-size="10" fill="#94A3B8"><text x="{left}" y="{height-25}">Less</text>{''.join(f'<rect x="{left+31+i*16}" y="{height-35}" width="11" height="11" rx="3" fill="{color}"/>' for i,color in enumerate(colors))}<text x="{left+113}" y="{height-25}">More</text></g>
</svg>"""
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(svg, encoding="utf-8")
