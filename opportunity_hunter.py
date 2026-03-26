#!/usr/bin/env python3
# ============================================================
#  OPPORTUNITY HUNTER v3.0 — github.com/thanasisgeorgoulas
#  Config-driven | HTML Dashboard | GitHub Actions ready
#  macOS Sequoia / Linux / GitHub Actions
# ============================================================

import requests
from bs4 import BeautifulSoup
import sqlite3, subprocess, hashlib, re, os, sys, tempfile, json
from datetime import datetime, date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not found. Run: pip install pyyaml")
    sys.exit(1)

# ─── Load Config ───────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        print(f"❌ config.yaml not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

CFG = load_config()
S   = CFG.get("settings", {})
N   = CFG.get("notifications", {})

DB_PATH        = SCRIPT_DIR / "data" / "seen.db"
LOG_PATH       = SCRIPT_DIR / "data" / "log.txt"
DASHBOARD_PATH = SCRIPT_DIR / "dashboard.html"
NOTE_FOLDER    = N.get("apple_notes_folder", "Opportunity Hunter")
DESC_MAX       = S.get("desc_max_length", 220)
IS_CI          = os.environ.get("CI") == "true"   # GitHub Actions detection

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Apple Silicon Mac OS X 15_0) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36"}

KEYWORDS_HIGH    = CFG.get("keywords_high", [])
KEYWORDS_MED     = CFG.get("keywords_medium", [])
KEYWORDS_UPCOMING = CFG.get("keywords_upcoming", [])
SOURCES          = CFG.get("sources", [])

MONTH_MAP = {
    "Ιανουαρίου":1,"Φεβρουαρίου":2,"Μαρτίου":3,"Απριλίου":4,
    "Μαΐου":5,"Ιουνίου":6,"Ιουλίου":7,"Αυγούστου":8,
    "Σεπτεμβρίου":9,"Οκτωβρίου":10,"Νοεμβρίου":11,"Δεκεμβρίου":12,
}

# ═══════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS seen (
        hash TEXT PRIMARY KEY, title TEXT, url TEXT,
        category TEXT, priority TEXT, source TEXT,
        found_date TEXT, deadline TEXT, is_upcoming INTEGER DEFAULT 0,
        description TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS deadlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, url TEXT, deadline_date TEXT,
        reminded_7d INTEGER DEFAULT 0,
        reminded_3d INTEGER DEFAULT 0,
        reminded_1d INTEGER DEFAULT 0
    )""")
    # Stats table
    c.execute("""CREATE TABLE IF NOT EXISTS stats (
        run_date TEXT PRIMARY KEY,
        total_found INTEGER DEFAULT 0,
        total_active INTEGER DEFAULT 0,
        total_upcoming INTEGER DEFAULT 0,
        sources_scraped INTEGER DEFAULT 0
    )""")
    conn.commit()
    return conn

def is_seen(conn, h):
    c = conn.cursor(); c.execute("SELECT 1 FROM seen WHERE hash=?", (h,))
    return c.fetchone() is not None

def mark_seen(conn, h, title, url, cat, pri, src, dl="", up=0, desc=""):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO seen
        (hash,title,url,category,priority,source,found_date,deadline,is_upcoming,description)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (h, title, url, cat, pri, src, date.today().isoformat(), dl, up, desc))
    conn.commit()

def save_deadline(conn, title, url, dl):
    if not dl: return
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO deadlines (title,url,deadline_date) VALUES (?,?,?)", (title,url,dl))
    conn.commit()

def save_stats(conn, total, active, upcoming, sources):
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO stats VALUES (?,?,?,?,?)""",
              (date.today().isoformat(), total, active, upcoming, sources))
    conn.commit()

def get_recent_history(conn, days=30):
    c = conn.cursor()
    c.execute("""SELECT found_date, category, COUNT(*) as cnt
                 FROM seen WHERE found_date >= date('now', ?)
                 GROUP BY found_date, category
                 ORDER BY found_date DESC""", (f"-{days} days",))
    return c.fetchall()

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def score_text(text):
    t = text.lower(); score = 0; matched = []
    for kw in KEYWORDS_HIGH:
        if str(kw).lower() in t: score += 10; matched.append(str(kw))
    for kw in KEYWORDS_MED:
        if str(kw).lower() in t: score += 5; matched.append(str(kw))
    return score, matched

def check_upcoming(text):
    t = text.lower()
    return any(str(kw).lower() in t for kw in KEYWORDS_UPCOMING)

def extract_deadline(text):
    patterns = [
        r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})",
        r"(\d{1,2})\s+(Ιανουαρίου|Φεβρουαρίου|Μαρτίου|Απριλίου|Μαΐου|Ιουνίου|"
        r"Ιουλίου|Αυγούστου|Σεπτεμβρίου|Οκτωβρίου|Νοεμβρίου|Δεκεμβρίου)\s+(\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                g = m.groups()
                if g[1] in MONTH_MAP:
                    dt = date(int(g[2]), MONTH_MAP[g[1]], int(g[0]))
                else:
                    d, mo, y = int(g[0]), int(g[1]), int(g[2])
                    if y < 100: y += 2000
                    dt = date(y, mo, d)
                if dt >= date.today(): return dt.isoformat()
            except: pass
    return ""

def fetch_description(url):
    if not S.get("fetch_descriptions", True):
        return ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, verify=False)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        cands = []
        for attr in [("name","description"),("property","og:description")]:
            t = soup.find("meta", attrs={attr[0]: attr[1]})
            if t and t.get("content","").strip(): cands.append(t["content"].strip())
        for sel in ["article p",".content p",".entry-content p","main p","p"]:
            t = soup.select_one(sel)
            if t:
                txt = t.get_text(strip=True)
                if len(txt) > 50: cands.append(txt); break
        if cands:
            best = max(cands, key=len)
            best = re.sub(r'\s+', ' ', best).strip()
            return best[:DESC_MAX] + ("…" if len(best) > DESC_MAX else "")
    except: pass
    return ""

def log(msg, level="INFO"):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    with open(LOG_PATH, "a", encoding="utf-8") as f: f.write(line + "\n")
    print(line)

def badge(p):
    return {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}.get(str(p),"⚪")

# ═══════════════════════════════════════════════════════════
#  SCRAPER
# ═══════════════════════════════════════════════════════════

def scrape(source):
    results = []
    try:
        r = requests.get(source["url"], headers=HEADERS, timeout=8, verify=False)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        for sel in [s.strip() for s in source["selector"].split(",")]:
            for tag in soup.select(sel):
                title = tag.get_text(strip=True)
                href  = tag.get("href", "")
                if not title or len(title) < 10 or not href: continue
                if href.startswith("/"): href = source["base_url"] + href
                elif not href.startswith("http"): href = source["base_url"] + "/" + href
                score, kw = score_text(title)
                if score == 0: continue
                h = hashlib.md5((title+href).encode()).hexdigest()
                results.append({
                    "hash": h, "title": title, "url": href,
                    "score": score, "keywords": kw,
                    "deadline": extract_deadline(title),
                    "is_upcoming": check_upcoming(title),
                    "category": source.get("category","📌 Άλλο"),
                    "priority": str(source.get("priority","MEDIUM")),
                    "source": source["name"], "description": "",
                })
    except Exception as e:
        log(f"ERROR scraping {source['name']}: {e}", "ERROR")
    seen_h, unique = set(), []
    for r in results:
        if r["hash"] not in seen_h: seen_h.add(r["hash"]); unique.append(r)
    return sorted(unique, key=lambda x: -x["score"])

# ═══════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

def ensure_notes_folder():
    if IS_CI or not N.get("apple_notes"): return
    s = f'tell application "Notes" to if not (exists folder "{NOTE_FOLDER}") then make new folder with properties {{name:"{NOTE_FOLDER}"}}'
    subprocess.run(["osascript","-e",s], capture_output=True)

def create_apple_note(title, html_body):
    if IS_CI or not N.get("apple_notes"): return False
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False)
    tmp.write(f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>{html_body}</body></html>')
    tmp.close()
    safe_t = title.replace('\\','\\\\').replace('"','\\"')
    script = f"""set nf to POSIX file "{tmp.name}"
set nc to read nf as «class utf8»
tell application "Notes"
    tell folder "{NOTE_FOLDER}"
        set nn to make new note with properties {{name:"{safe_t}"}}
        set body of nn to nc
    end tell
end tell"""
    result = subprocess.run(["osascript","-e",script], capture_output=True, text=True)
    os.unlink(tmp.name)
    if result.returncode != 0: log(f"AppleScript error: {result.stderr.strip()}", "WARN"); return False
    return True

def mac_notify(title, sub, msg):
    if IS_CI or not N.get("mac_notification"): return
    t = title[:60].replace('"',"'"); s = sub[:60].replace('"',"'"); m = msg[:100].replace('"',"'")
    subprocess.run(["osascript","-e",f'display notification "{m}" with title "{t}" subtitle "{s}" sound name "Glass"'], capture_output=True)

def telegram_notify(text):
    if not N.get("telegram_enabled"): return
    token = N.get("telegram_token") or os.environ.get("TELEGRAM_TOKEN","")
    chat_id = N.get("telegram_chat_id") or os.environ.get("TELEGRAM_CHAT_ID","")
    if not token or not chat_id: return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                      timeout=10)
        log("✅ Telegram notification sent")
    except Exception as e:
        log(f"Telegram error: {e}", "WARN")

def check_deadlines(conn):
    c = conn.cursor()
    c.execute("SELECT id,title,url,deadline_date,reminded_7d,reminded_3d,reminded_1d FROM deadlines WHERE deadline_date >= ?", (date.today().isoformat(),))
    for did, title, url, dl_str, r7, r3, r1 in c.fetchall():
        try:
            days = (date.fromisoformat(dl_str) - date.today()).days
            msg = f"⏰ Deadline: {title[:60]}\n{url}"
            if   days <= 1 and not r1:
                mac_notify("⏰ DEADLINE ΑΥΡΙΟ!", title[:50], url[:80])
                telegram_notify(f"⏰ <b>DEADLINE ΑΥΡΙΟ!</b>\n{title}\n{url}")
                c.execute("UPDATE deadlines SET reminded_1d=1 WHERE id=?", (did,))
            elif days <= 3 and not r3:
                mac_notify("⚠️ Deadline σε 3 μέρες", title[:50], dl_str)
                telegram_notify(f"⚠️ <b>Deadline σε 3 μέρες</b>\n{title}\n📅 {dl_str}")
                c.execute("UPDATE deadlines SET reminded_3d=1 WHERE id=?", (did,))
            elif days <= 7 and not r7:
                mac_notify("📅 Deadline σε 7 μέρες", title[:50], dl_str)
                telegram_notify(f"📅 <b>Deadline σε 7 μέρες</b>\n{title}\n📅 {dl_str}")
                c.execute("UPDATE deadlines SET reminded_7d=1 WHERE id=?", (did,))
        except: pass
    conn.commit()

# ═══════════════════════════════════════════════════════════
#  HTML DASHBOARD
# ═══════════════════════════════════════════════════════════

def build_dashboard(today_str, active, upcoming, by_cat, history):
    # Category stats για charts
    cat_stats = {cat: len(items) for cat, items in by_cat.items()}
    cat_json  = json.dumps(cat_stats, ensure_ascii=False)

    # History JSON για sparkline
    hist_by_date = {}
    for row in history:
        d, cat, cnt = row
        hist_by_date[d] = hist_by_date.get(d, 0) + cnt
    hist_json = json.dumps(hist_by_date, ensure_ascii=False)

    def card(item):
        pb = badge(item["priority"])
        dl = f'<span class="deadline">⏰ Deadline: {item["deadline"]}</span>' if item.get("deadline") else ""
        up = '<span class="tag upcoming-tag">🔮 Προσεχές</span>' if item.get("is_upcoming") else ""
        kws = " ".join([f'<span class="tag">{k}</span>' for k in item["keywords"][:4]])
        desc = f'<p class="desc">{item["description"]}</p>' if item.get("description") else '<p class="desc muted">Άνοιξε το link για λεπτομέρειες.</p>'
        pri_class = {"HIGH":"priority-high","MEDIUM":"priority-med","LOW":"priority-low"}.get(item["priority"],"priority-med")
        return f"""
        <div class="card {pri_class}" data-category="{item['category']}" data-priority="{item['priority']}" data-title="{item['title'].lower()}">
            <div class="card-header">
                <span class="badge">{pb}</span>
                <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
                {up}
            </div>
            {desc}
            <div class="card-footer">
                <span class="source">📡 {item['source']}</span>
                {dl}
                <div class="tags">{kws}</div>
            </div>
        </div>"""

    all_cards = ""
    for cat, items in sorted(by_cat.items()):
        all_cards += f'<div class="section-header"><h2>{cat} <span class="count">{len(items)}</span></h2></div>'
        for item in items[:S.get("max_items_per_category", 12)]:
            all_cards += card(item)

    upcoming_cards = ""
    if upcoming:
        for item in sorted(upcoming, key=lambda x: -x["score"])[:S.get("max_upcoming_items", 10)]:
            upcoming_cards += card(item)

    profile = CFG.get("profile", {})

    return f"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎯 Opportunity Hunter — {today_str}</title>
<style>
  :root {{
    --bg: #0f1117; --surface: #1a1d27; --surface2: #22263a;
    --accent: #6c63ff; --accent2: #00d4aa; --danger: #ff4757;
    --warn: #ffa502; --text: #e8eaf0; --muted: #7a7f9a;
    --border: #2e3248; --radius: 12px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: var(--bg); color: var(--text); min-height: 100vh; }}
  .topbar {{ background: var(--surface); border-bottom: 1px solid var(--border);
             padding: 16px 24px; display: flex; align-items: center; gap: 16px;
             position: sticky; top: 0; z-index: 100; }}
  .topbar h1 {{ font-size: 1.2rem; font-weight: 700; }}
  .topbar .meta {{ color: var(--muted); font-size: 0.85rem; margin-left: auto; }}
  .stats-row {{ display: flex; gap: 12px; padding: 20px 24px; flex-wrap: wrap; }}
  .stat-card {{ background: var(--surface); border: 1px solid var(--border);
                border-radius: var(--radius); padding: 16px 20px; flex: 1; min-width: 140px; }}
  .stat-card .num {{ font-size: 2rem; font-weight: 800; color: var(--accent); }}
  .stat-card .label {{ font-size: 0.8rem; color: var(--muted); margin-top: 4px; }}
  .controls {{ padding: 0 24px 16px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
  .search {{ flex: 1; min-width: 200px; background: var(--surface); border: 1px solid var(--border);
             border-radius: 8px; padding: 10px 14px; color: var(--text); font-size: 0.9rem; outline: none; }}
  .search:focus {{ border-color: var(--accent); }}
  .filter-btn {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
                 padding: 8px 14px; color: var(--text); cursor: pointer; font-size: 0.85rem;
                 transition: all 0.2s; }}
  .filter-btn:hover, .filter-btn.active {{ background: var(--accent); border-color: var(--accent); }}
  .upcoming-section {{ margin: 0 24px 8px; background: linear-gradient(135deg, #1a1547, #1a2a47);
                       border: 1px solid #3d3480; border-radius: var(--radius); padding: 20px; }}
  .upcoming-section h2 {{ color: #a78bfa; margin-bottom: 16px; }}
  .grid {{ padding: 0 24px 40px; display: grid;
           grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 14px; }}
  .section-header {{ grid-column: 1/-1; margin-top: 12px; }}
  .section-header h2 {{ font-size: 1rem; color: var(--muted); padding: 8px 0;
                        border-bottom: 1px solid var(--border); }}
  .count {{ background: var(--accent); color: white; border-radius: 20px;
            padding: 2px 8px; font-size: 0.75rem; margin-left: 8px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border);
           border-radius: var(--radius); padding: 16px; transition: all 0.2s;
           display: flex; flex-direction: column; gap: 10px; }}
  .card:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 4px 20px rgba(108,99,255,0.15); }}
  .card.priority-high {{ border-left: 3px solid var(--danger); }}
  .card.priority-med  {{ border-left: 3px solid var(--warn); }}
  .card.priority-low  {{ border-left: 3px solid var(--accent2); }}
  .card-header {{ display: flex; align-items: flex-start; gap: 10px; }}
  .card-header h3 {{ font-size: 0.92rem; line-height: 1.4; flex: 1; }}
  .card-header h3 a {{ color: var(--text); text-decoration: none; }}
  .card-header h3 a:hover {{ color: var(--accent); }}
  .badge {{ font-size: 1.1rem; flex-shrink: 0; }}
  .desc {{ font-size: 0.82rem; color: var(--muted); line-height: 1.5; }}
  .muted {{ font-style: italic; }}
  .card-footer {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: auto; }}
  .source {{ font-size: 0.75rem; color: var(--muted); }}
  .deadline {{ font-size: 0.75rem; color: var(--warn); font-weight: 600; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-left: auto; }}
  .tag {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 4px;
          padding: 2px 6px; font-size: 0.7rem; color: var(--muted); }}
  .upcoming-tag {{ background: #2d1f6e; border-color: #6c63ff; color: #a78bfa; }}
  .hidden {{ display: none !important; }}
  .no-results {{ grid-column: 1/-1; text-align: center; padding: 40px; color: var(--muted); }}
  @media (max-width: 600px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="topbar">
  <h1>🎯 Opportunity Hunter</h1>
  <div class="meta">📅 {today_str} &nbsp;|&nbsp; {CFG.get('profile', {}).get('name','')}</div>
</div>

<div class="stats-row">
  <div class="stat-card"><div class="num">{len(active)}</div><div class="label">Ενεργές Ευκαιρίες</div></div>
  <div class="stat-card"><div class="num" style="color:var(--warn)">{len([x for x in active if x['priority']=='HIGH'])}</div><div class="label">Υψηλή Προτεραιότητα</div></div>
  <div class="stat-card"><div class="num" style="color:#a78bfa">{len(upcoming)}</div><div class="label">Προσεχή Προγράμματα</div></div>
  <div class="stat-card"><div class="num" style="color:var(--accent2)">{len(SOURCES)}</div><div class="label">Sites Παρακολούθησης</div></div>
</div>

<div class="controls">
  <input class="search" type="text" placeholder="🔍 Αναζήτηση..." id="searchInput" oninput="filterCards()">
  <button class="filter-btn active" onclick="filterPriority('ALL', this)">Όλα</button>
  <button class="filter-btn" onclick="filterPriority('HIGH', this)">🔴 Υψηλή</button>
  <button class="filter-btn" onclick="filterPriority('MEDIUM', this)">🟡 Μεσαία</button>
  <button class="filter-btn" onclick="filterPriority('LOW', this)">🟢 Χαμηλή</button>
</div>

{'<div class="upcoming-section"><h2>🔮 Προσεχή — Δεν έχουν ανοίξει ακόμα</h2><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px">' + upcoming_cards + '</div></div>' if upcoming else ''}

<div class="grid" id="cardsGrid">
  {all_cards}
  <div class="no-results hidden" id="noResults">Δεν βρέθηκαν αποτελέσματα.</div>
</div>

<script>
let activePriority = 'ALL';

function filterCards() {{
  const q = document.getElementById('searchInput').value.toLowerCase();
  const cards = document.querySelectorAll('#cardsGrid .card');
  let visible = 0;
  cards.forEach(card => {{
    const title    = card.dataset.title || '';
    const priority = card.dataset.priority || '';
    const matchQ   = !q || title.includes(q) || card.innerText.toLowerCase().includes(q);
    const matchP   = activePriority === 'ALL' || priority === activePriority;
    if (matchQ && matchP) {{ card.classList.remove('hidden'); visible++; }}
    else card.classList.add('hidden');
  }});
  document.getElementById('noResults').classList.toggle('hidden', visible > 0);
  // Hide empty section headers
  document.querySelectorAll('#cardsGrid .section-header').forEach(h => {{
    let next = h.nextElementSibling;
    let hasVisible = false;
    while (next && !next.classList.contains('section-header')) {{
      if (!next.classList.contains('hidden') && next.classList.contains('card')) hasVisible = true;
      next = next.nextElementSibling;
    }}
    h.classList.toggle('hidden', !hasVisible);
  }});
}}

function filterPriority(p, btn) {{
  activePriority = p;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterCards();
}}
</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════
#  APPLE NOTE HTML BODY
# ═══════════════════════════════════════════════════════════

def build_note_html(today_str, active, upcoming, by_cat):
    h = []
    h.append(f'<p><b>📅 {today_str}</b> | <b>{len(active)}</b> ενεργές · <b>{len(upcoming)}</b> προσεχείς</p><hr/>')
    if upcoming:
        h.append('<h2>🔮 ΠΡΟΣΕΧΗ</h2>')
        for i in sorted(upcoming, key=lambda x: -x["score"])[:10]:
            h.append(f'<h3>{badge(i["priority"])} {i["title"]}</h3>')
            if i.get("description"): h.append(f'<p>{i["description"]}</p>')
            h.append(f'<p>🔗 {i["url"]}</p>')
            if i.get("deadline"): h.append(f'<p>⏰ <b>Αναμ. έναρξη:</b> {i["deadline"]}</p>')
            h.append(f'<p>🏷 {", ".join(i["keywords"][:4])} | 📡 {i["source"]}</p><br/>')
        h.append('<hr/>')
    h.append('<h2>✅ ΕΝΕΡΓΕΣ ΕΥΚΑΙΡΙΕΣ</h2>')
    for cat, items in sorted(by_cat.items()):
        h.append(f'<h2>{cat}</h2>')
        for i in items[:S.get("max_items_per_category", 12)]:
            h.append(f'<h3>{badge(i["priority"])} {i["title"]}</h3>')
            h.append(f'<p>{i.get("description") or "<i>Άνοιξε το link για λεπτομέρειες.</i>"}</p>')
            h.append(f'<p>🔗 {i["url"]}</p>')
            if i.get("deadline"): h.append(f'<p>⏰ <b>Deadline:</b> {i["deadline"]}</p>')
            h.append(f'<p>🏷 {", ".join(i["keywords"][:4])} | 📡 {i["source"]}</p><br/>')
        h.append('<hr/>')
    return "\n".join(h)

# ═══════════════════════════════════════════════════════════
#  TELEGRAM SUMMARY
# ═══════════════════════════════════════════════════════════

def build_telegram_summary(active, upcoming):
    high = [x for x in active if x["priority"] == "HIGH"]
    lines = [f"🎯 <b>Opportunity Hunter — {date.today().strftime('%d/%m/%Y')}</b>",
             f"📊 {len(active)} ενεργές · {len(upcoming)} προσεχείς · {len(high)} υψηλής προτ.\n"]
    for item in high[:5]:
        dl = f" | ⏰ {item['deadline']}" if item.get("deadline") else ""
        lines.append(f"{badge(item['priority'])} <b>{item['title'][:60]}</b>{dl}")
        lines.append(f"🔗 {item['url']}\n")
    if len(high) > 5:
        lines.append(f"… και {len(high)-5} ακόμα υψηλής προτεραιότητας.")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main():
    import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    env = "GitHub Actions" if IS_CI else "Local"
    log(f"{'='*60}")
    log(f"🔍 Opportunity Hunter v3.0 [{env}] — {date.today().isoformat()}")
    log(f"{'='*60}")

    conn = init_db()
    ensure_notes_folder()
    check_deadlines(conn)

    all_new, active, upcoming = [], [], []

    for source in SOURCES:
        log(f"  ↳ {source['name']} …")
        nc = 0
        for item in scrape(source):
            if not is_seen(conn, item["hash"]):
                if S.get("fetch_descriptions", True):
                    item["description"] = fetch_description(item["url"])
                mark_seen(conn, item["hash"], item["title"], item["url"],
                          item["category"], item["priority"], item["source"],
                          item["deadline"], int(item["is_upcoming"]), item["description"])
                if item["deadline"]:
                    save_deadline(conn, item["title"], item["url"], item["deadline"])
                all_new.append(item); nc += 1
                (upcoming if item["is_upcoming"] else active).append(item)
        if nc > 0: log(f"     → {nc} νέα")

    save_stats(conn, len(all_new), len(active), len(upcoming), len(SOURCES))
    history = get_recent_history(conn)

    if not all_new:
        log("✅ Δεν βρέθηκαν νέες ευκαιρίες σήμερα.")
        dashboard_link = f"file:///Users/thanasis/OpportunityHunter/dashboard.html"
        mac_notify("Opportunity Hunter", "✅ Ολοκληρώθηκε", f"📊 {dashboard_link}")
        today_str = date.today().strftime("%d/%m/%Y")
        dashboard_html = build_dashboard(today_str, [], [], {}, [])
        DASHBOARD_PATH.write_text(dashboard_html, encoding="utf-8")
        log(f"✅ Dashboard: {DASHBOARD_PATH}")
        conn.close(); return

    by_cat = {}
    for item in sorted(active, key=lambda x: -x["score"]):
        by_cat.setdefault(item["category"], []).append(item)

    today_str = date.today().strftime("%d/%m/%Y")

    # ── HTML Dashboard ──
    if N.get("html_dashboard", True):
        dashboard_html = build_dashboard(today_str, active, upcoming, by_cat, history)
        DASHBOARD_PATH.write_text(dashboard_html, encoding="utf-8")
        log(f"✅ Dashboard: {DASHBOARD_PATH}")
        if N.get("dashboard_auto_open") and not IS_CI:
            subprocess.run(["open", str(DASHBOARD_PATH)], capture_output=True)

    # ── Apple Notes ──
    note_title = f"🎯 Ευκαιρίες {today_str} — {len(active)} ενεργές · {len(upcoming)} προσεχείς"
    note_html  = build_note_html(today_str, active, upcoming, by_cat)
    if create_apple_note(note_title, note_html):
        log(f"✅ Apple Note: {note_title}")
    elif not IS_CI:
        log("⚠️  Apple Note failed — opening dashboard in browser")
        subprocess.run(["open", str(DASHBOARD_PATH)], capture_output=True)

    # ── Mac Notification ──
    high_count = len([x for x in all_new if x["priority"] == "HIGH"])
    dashboard_link = f"file:///Users/thanasis/OpportunityHunter/dashboard.html"
    mac_notify("🎯 Opportunity Hunter",
               f"{len(all_new)} νέες ευκαιρίες! 🔴 Υψηλή:{high_count}",
               f"📊 {dashboard_link}")

    # ── Telegram ──
    telegram_notify(build_telegram_summary(active, upcoming))

    # ── Summary ──
    log(f"\n📊 Σύνολο={len(all_new)} | Ενεργά={len(active)} | Προσεχή={len(upcoming)} | Υψηλή={high_count}")
    for cat, items in sorted(by_cat.items()):
        log(f"   {cat}: {len(items)}")

    conn.close()
    log("✅ Ολοκληρώθηκε.\n")

if __name__ == "__main__":
    main()
