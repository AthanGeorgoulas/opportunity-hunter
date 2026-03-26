#!/bin/bash
# ============================================================
#  SETUP — Opportunity Hunter για macOS (M4 / Sequoia)
#  Τρέξε μία φορά από Terminal
# ============================================================

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Opportunity Hunter — Setup v1.0         ║"
echo "║  Athanasios Georgoulas                   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Βήμα 1: Homebrew ──────────────────────────────────────
echo "🍺 [1/5] Έλεγχος Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "  → Εγκατάσταση Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # M4 path
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo "  ✅ Homebrew εγκαταστάθηκε."
else
    echo "  ✅ Homebrew ήδη εγκατεστημένο."
fi

# ── Βήμα 2: Python ────────────────────────────────────────
echo ""
echo "🐍 [2/5] Έλεγχος Python..."
if ! command -v python3 &>/dev/null || [[ $(python3 --version 2>&1) < "Python 3.10" ]]; then
    echo "  → Εγκατάσταση Python 3.12..."
    brew install python@3.12
    echo "  ✅ Python εγκαταστάθηκε."
else
    echo "  ✅ Python ήδη εγκατεστημένο: $(python3 --version)"
fi

# ── Βήμα 3: Python packages ───────────────────────────────
echo ""
echo "📦 [3/5] Εγκατάσταση Python packages..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install requests beautifulsoup4 lxml urllib3 --quiet
echo "  ✅ Packages εγκαταστάθηκαν."

# ── Βήμα 4: Δομή φακέλων ─────────────────────────────────
echo ""
echo "📁 [4/5] Δημιουργία φακέλων..."
mkdir -p ~/OpportunityHunter
mkdir -p ~/Library/LaunchAgents

# Αντιγραφή script
SCRIPT_DEST=~/OpportunityHunter/opportunity_hunter.py
if [ -f "./opportunity_hunter.py" ]; then
    cp ./opportunity_hunter.py "$SCRIPT_DEST"
    echo "  ✅ Script αντιγράφηκε στο ~/OpportunityHunter/"
else
    echo "  ⚠️  Δεν βρέθηκε opportunity_hunter.py στον τρέχοντα φάκελο."
    echo "     Αντίγραψέ το χειροκίνητα στο: ~/OpportunityHunter/"
fi

chmod +x "$SCRIPT_DEST" 2>/dev/null || true

# ── Βήμα 5: LaunchAgent (καθημερινό 08:30) ───────────────
echo ""
echo "⏰ [5/5] Ρύθμιση αυτόματης εκτέλεσης (08:30 κάθε μέρα)..."

PYTHON_PATH=$(which python3)
PLIST_PATH=~/Library/LaunchAgents/com.thanasis.opportunityhunter.plist

cat > "$PLIST_PATH" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thanasis.opportunityhunter</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${HOME}/OpportunityHunter/opportunity_hunter.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>${HOME}/OpportunityHunter/launchd_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${HOME}/OpportunityHunter/launchd_stderr.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST_EOF

# Load το LaunchAgent
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "  ✅ LaunchAgent φορτώθηκε — τρέχει κάθε μέρα στις 08:30."

# ── Τελικό μήνυμα ─────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ SETUP ΟΛΟΚΛΗΡΩΘΗΚΕ!                  ║"
echo "╠══════════════════════════════════════════╣"
echo "║                                          ║"
echo "║  Αρχεία:                                 ║"
echo "║  ~/OpportunityHunter/                    ║"
echo "║    opportunity_hunter.py  ← το script   ║"
echo "║    seen.db                ← ιστορικό    ║"
echo "║    log.txt                ← logs        ║"
echo "║                                          ║"
echo "║  Εκτέλεση κάθε μέρα: 08:30              ║"
echo "║  Αποτελέσματα: Apple Notes               ║"
echo "║  Folder: 'Opportunity Hunter'            ║"
echo "║                                          ║"
echo "║  Χειροκίνητη εκτέλεση (test):            ║"
echo "║  python3 ~/OpportunityHunter/            ║"
echo "║          opportunity_hunter.py           ║"
echo "║                                          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
