import json
import pathlib
import re
import subprocess
from datetime import datetime

README = pathlib.Path("README.md")
START = "<!-- RECENT:START -->"
END = "<!-- RECENT:END -->"
USER = "Alkhirza"
MAX_ROWS = 8

raw = subprocess.check_output([
    "gh", "repo", "list", USER,
    "--visibility", "public",
    "--source",                      # skip forks
    "--limit", "30",
    "--json", "name,description,url,primaryLanguage,pushedAt",
])
repos = [r for r in json.loads(raw) if r["name"] != USER]
repos.sort(key=lambda r: r["pushedAt"], reverse=True)

rows = [
    "| Repo | Language | Description | Last push |",
    "|---|---|---|---|",
]
for r in repos[:MAX_ROWS]:
    lang = (r["primaryLanguage"] or {}).get("name", "-")
    desc = (r["description"] or "-").replace("|", "\\|")
    pushed = datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
    rows.append(f"| [{r['name']}]({r['url']}) | {lang} | {desc} | {pushed} |")

block = START + "\n" + "\n".join(rows) + "\n" + END

text = README.read_text(encoding="utf-8")
pattern = re.escape(START) + r".*?" + re.escape(END)
new_text = re.sub(pattern, lambda _: block, text, flags=re.S)

if new_text != text:
    README.write_text(new_text, encoding="utf-8")
    print("README updated")
else:
    print("No changes")