
-----

# 🎯 Opportunity Hunter

> An automated system that daily scouts for grants, benefits, job openings, and scholarships — delivering them directly to your Telegram every morning.

-----

## Overview

Every morning at 09:00 (local time), the system automatically:

1.  **Scans 19+ sources** (DYPA, ESPA, EURES, Türkiye Scholarships, major job boards, etc.).
2.  **Filters results** based on your specific keywords.
3.  **Deduplicates data** — you only see NEW opportunities, never repeats.
4.  **Sends a Telegram notification** with the top matches.
5.  **Generates an HTML Dashboard** featuring search and filter capabilities.
6.  **Tracks deadlines** with reminders 7, 3, and 1 day before expiration.

-----

## Installation Guide — Step by Step

> ✅ Beginner-friendly — no prior programming experience required.

### Part 1: Download the Code

**Step 1.** Open your Terminal:

  - **macOS:** Press `Cmd + Space`, type `Terminal`, hit Enter.
  - **Windows:** Press `Win + R`, type `cmd`, hit Enter.

**Step 2.** Clone the project:

```bash
git clone https://github.com/AthanGeorgoulas/opportunity-hunter.git
cd opportunity-hunter
```

> ⚠️ If you see a "git not found" error: download Git from [git-scm.com/downloads](https://git-scm.com/downloads).

-----

### Part 2: Python Setup

**macOS:**

```bash
# Check version:
python3 --version
```

If you see `Python 3.x.x`, you are ready. Otherwise, install via Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12
```

**Windows:**

1.  Visit [python.org/downloads](https://python.org/downloads).
2.  Download Python 3.12.
3.  During installation, check **"Add Python to PATH"** ✅.
4.  Restart your computer.

**Step 3.** Install dependencies:

```bash
pip3 install -r requirements.txt
```

-----

### Part 3: Configure Your Profile

**Step 4.** Create your configuration file:

```bash
cp config.example.yaml config.yaml
```

**Step 5.** Open `config.yaml` for editing:

  - **macOS:** `open -e config.yaml`
  - **Windows:** `notepad config.yaml`

**Step 6.** Update your personal details:

```yaml
profile:
  name: "Your Name"
  age: 25                         # Your age
  status: "student"               # unemployed / employed / student
  dypa_card: false                # true if you have a DYPA unemployment card
  income_annual: 12000            # annual income in EUR
```

**Step 7.** Add relevant keywords:

```yaml
keywords_high:
  - "informatics"
  - "engineer"
  - "renewable"
  - "scholarship"
  - "espa"
  - "internship"
```

> 💡 **Tip:** Use word stems (e.g., "engin" instead of "engineering") to catch both singular and plural results.

-----

### Part 4: Telegram Setup (Mobile Notifications)

**Step 8.** Create a Telegram Bot:

1.  Open Telegram and search for **@BotFather**.
2.  Type `/newbot` and follow the prompts.
3.  Copy the **API Token** (e.g., `1234567890:AAF-xyz...`).

**Step 9.** Find your Chat ID:

1.  Search for **@userinfobot** in Telegram.
2.  Type `/start`.
3.  Copy the numerical **Id** (e.g., `987654321`).

**Step 10.** Update `config.yaml`:

```yaml
notifications:
  telegram_enabled: true
  telegram_token: "YOUR_TOKEN_HERE"
  telegram_chat_id: "YOUR_CHAT_ID_HERE"
```

-----

### Part 5: Initial Test

**Step 11.** Run the script:

```bash
python3 opportunity_hunter.py
```

Check your Telegram: you should receive a message with current opportunities\!
Check the Dashboard: Open `dashboard.html` in your browser.

-----

### Part 6: Automation

**macOS (Auto-run at 09:00):**

```bash
chmod +x setup.sh && ./setup.sh
```

**Windows (Task Scheduler):**

1.  Open "Task Scheduler".
2.  Create Basic Task -\> Daily -\> 09:00.
3.  Action: Start a program -\> `python`.
4.  Arguments: `C:\path\to\opportunity-hunter\opportunity_hunter.py`.

-----

### Part 7: Cloud Deployment (GitHub Actions)

To run the hunter even when your computer is off:

1.  **Fork** this repository.
2.  Go to **Settings \> Secrets and variables \> Actions**.
3.  Add two New repository secrets:
      - `TELEGRAM_TOKEN`
      - `TELEGRAM_CHAT_ID`
4.  Go to the **Actions** tab and enable the "Daily Opportunity Hunt" workflow.

-----

## Project Structure

```text
opportunity-hunter/
├── opportunity_hunter.py    ← Main script logic
├── config.example.yaml      ← Configuration template
├── config.yaml              ← Your private settings (GIT-IGNORED)
├── requirements.txt         ← Required Python libraries
├── setup.sh                 ← macOS automation script
├── dashboard.html           ← Auto-generated visual results
└── .github/workflows/
    └── daily.yml            ← GitHub Actions automation
```

-----

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

-----

*Built with Python 🐍 | Helping students and professionals find their next big move across Greece and Europe.*

-----
