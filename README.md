# 🎯 Opportunity Hunter

> A free, automated daily scraper that monitors Greek government subsidies, EU funding programs, job opportunities, and scholarships — delivering results to your Apple Notes or a local HTML dashboard.

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-green?logo=githubactions)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Cloud-lightgrey)

---

## 📌 What It Does

Every morning at 08:30, Opportunity Hunter automatically:

1. Scrapes **19+ websites** (DYPA, ESPA, EURES, Türkiye Scholarships, job boards, and more)
2. Scores each result using **keyword matching** based on your profile in `config.yaml`
3. Stores only **new results** — never repeats what you have already seen (SQLite memory)
4. Fetches a **short description** for each opportunity by visiting its page
5. Separates **upcoming programs** (not yet open) from active ones
6. Tracks **deadlines** and sends reminders 7, 3, and 1 day before expiry
7. Writes a formatted **Apple Note** with all results (macOS)
8. Generates a **dark-themed HTML dashboard** with live search and filters
9. Sends a **Mac notification** with a daily summary
10. Optionally sends a **Telegram message** with top results

---

## 🖥️ Dashboard

After each run, `dashboard.html` is generated locally:

- Real-time search across all results
- Priority filters: High / Medium / Low
- Separate section for upcoming programs not yet open
- Deadline indicators per result
- Mobile-friendly dark theme

```bash
open dashboard.html
```

---

## 🚀 Quick Start

### macOS

```bash
# 1. Clone
git clone https://github.com/AthanGeorgoulas/opportunity-hunter.git
cd opportunity-hunter

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Edit your profile
nano config.yaml

# 4. Run manually to test
python3 opportunity_hunter.py

# 5. Install daily scheduler (runs at 08:30 automatically)
chmod +x setup.sh && ./setup.sh
```

### Linux / GitHub Actions (cloud)

See the GitHub Actions section below.

---

## ⚙️ Configuration

**You only ever need to edit `config.yaml`. Never touch the Python script.**

```yaml
profile:
  name: "Your Name"
  status: "unemployed"       # unemployed / employed / student
  dypa_card: true            # Active DYPA (Greek unemployment office) card
  income_annual: 5000
  target_countries:
    - "Greece"
    - "Turkey"
    - "Remote"

keywords_high:               # Score +10 per match
  - "voucher"
  - "scholarship"
  - "espa"
  - "turkey"

keywords_medium:             # Score +5 per match
  - "internship"
  - "remote"
  - "master"

notifications:
  apple_notes: true
  html_dashboard: true
  dashboard_auto_open: false
  telegram_enabled: false
  telegram_token: ""
  telegram_chat_id: ""

schedule:
  hour: 8
  minute: 30
```

### Adding a Custom Source

```yaml
sources:
  - name: "My Site"
    url: "https://example.com/news"
    selector: "h2 a, h3 a, article a"
    base_url: "https://example.com"
    category: "📌 Custom"
    priority: HIGH
```

---

## 📡 Sources Monitored (19 total)

| Category | Sites |
|---|---|
| Greek Government | DYPA, gov.gr, OPEKA, TEE, Region of Central Macedonia, Startup Greece |
| EU Funds (ESPA) | espa.gr, antagonistikotita.gr |
| European | EURES, EURAXESS, EU Youth Portal |
| Turkey | Türkiye Scholarships, TÜBİTAK |
| Jobs | Kariera.gr, Skywalker.gr |
| News | Epixeiro, Newmoney, Opportunity Desk |

---

## ☁️ GitHub Actions

Run the hunter daily on GitHub servers — even when your computer is off.

**Setup:**
1. Fork this repository
2. Go to **Settings → Secrets → Actions** and add (optional): `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
3. Go to **Actions → Daily Opportunity Hunt → Enable workflow**

The workflow runs at **08:00 UTC** daily and commits `dashboard.html` automatically.

**Manual trigger:** Actions → Daily Opportunity Hunt → Run workflow

---

## 📁 Project Structure

```
opportunity-hunter/
├── opportunity_hunter.py   ← Main script
├── config.yaml             ← Your profile (only file you edit)
├── requirements.txt
├── setup.sh                ← macOS scheduler installer
├── dashboard.html          ← Auto-generated after each run
├── data/
│   ├── seen.db             ← SQLite history (auto-created)
│   └── log.txt             ← Run logs (auto-created)
└── .github/
    └── workflows/
        └── daily.yml       ← GitHub Actions workflow
```

---

## 📲 Telegram Setup (Optional)

1. Open Telegram → search **@BotFather** → `/newbot`
2. Copy the token → set `telegram_token` in `config.yaml`
3. Get your chat ID from **@userinfobot**
4. Set `telegram_enabled: true`

---

## ⏰ macOS Scheduler

`setup.sh` installs a LaunchAgent that runs the script daily at your configured time.

```bash
# Check status
launchctl list | grep opportunityhunter

# Disable
launchctl unload ~/Library/LaunchAgents/com.opportunityhunter.plist

# Re-enable
launchctl load ~/Library/LaunchAgents/com.opportunityhunter.plist
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| Apple Notes not creating | System Settings → Privacy & Security → Automation → Terminal → Notes → Enable |
| No Mac notifications | System Settings → Notifications → Terminal → Allow |
| Script not running automatically | Re-run `setup.sh` |
| SSL errors in log | Normal for some Greek sites — handled automatically |
| Too many irrelevant results | Change `if score == 0` to `if score < 10` in the script |

---

## 🤝 Contributing

Pull requests welcome. Ideas:
- Email notification support
- Windows/Linux scheduler equivalent
- Web UI for `config.yaml`
- Additional country sources

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built with Python | For job seekers, students, and professionals navigating Greek and European funding opportunities.*
