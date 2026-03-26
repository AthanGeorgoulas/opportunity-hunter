# 🎯 Opportunity Hunter

> Αυτόματο σύστημα παρακολούθησης επιδοτήσεων, επιδομάτων, θέσεων εργασίας και ευκαιριών για Ελλάδα, ΕΕ και Τουρκία.

![GitHub Actions](https://github.com/YOUR_USERNAME/opportunity-hunter/actions/workflows/daily.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Τι κάνει

- 🔍 Scrapes **19+ sites** καθημερινά (ΔΥΠΑ, ΕΣΠΑ, EURES, Türkiye Scholarships, κλπ)
- 🧠 **Keyword scoring** βάσει του προφίλ σου — βλέπεις μόνο ό,τι σε αφορά
- 🆕 **Μόνο νέα αποτελέσματα** — δεν επαναλαμβάνει παλιά (SQLite memory)
- 📄 **Σύντομη περιγραφή** για κάθε ευκαιρία
- 🔮 **Προσεχή προγράμματα** — ευκαιρίες που δεν έχουν ανοίξει ακόμα
- ⏰ **Deadline reminders** — 7, 3 και 1 μέρα πριν
- 📊 **HTML Dashboard** με search, φίλτρα, dark theme
- 🍎 **Apple Notes** integration (macOS)
- ☁️ **GitHub Actions** — τρέχει στο cloud ακόμα κι αν ο υπολογιστής είναι κλειστός
- 📱 **Telegram notifications** (προαιρετικό)

---

## 🚀 Quick Start

### macOS (local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/opportunity-hunter.git
cd opportunity-hunter

# 2. Install
pip install -r requirements.txt

# 3. Ρύθμισε το προφίλ σου
nano config.yaml

# 4. Τρέξε
python opportunity_hunter.py

# 5. Αυτόματη εκτέλεση κάθε μέρα 08:30
chmod +x setup.sh && ./setup.sh
```

### GitHub Actions (cloud)

1. Fork το repo
2. Πήγαινε **Settings → Secrets → Actions**
3. Πρόσθεσε (προαιρετικά): `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
4. Πήγαινε **Actions → Daily Opportunity Hunt → Enable**
5. Τρέχει αυτόματα κάθε μέρα στις 10:00 (Ελλάδα)

---

## ⚙️ Ρύθμιση Προφίλ (`config.yaml`)

```yaml
profile:
  name: "Το Όνομά σου"
  age: 25
  status: "unemployed"     # unemployed / employed / student
  dypa_card: true
  income_annual: 5000

keywords_high:
  - "τηλεπικοινωνι"
  - "voucher"
  - "εσπα"
  # ... πρόσθεσε τα δικά σου

notifications:
  apple_notes: true        # macOS μόνο
  telegram_enabled: false  # true + βάλε token για Telegram
  html_dashboard: true     # Παράγει dashboard.html
```

---

## 📊 Dashboard

Μετά από κάθε εκτέλεση δημιουργείται `dashboard.html`:

- **Search** σε πραγματικό χρόνο
- **Φίλτρα** ανά προτεραιότητα (🔴/🟡/🟢)
- **Ξεχωριστή ενότητα** για Προσεχή Προγράμματα
- **Dark theme**, mobile-friendly

Άνοιξέ το με: `open dashboard.html`

---

## 🗂️ Δομή

```
opportunity-hunter/
├── opportunity_hunter.py   ← Κύριο script
├── config.yaml             ← Το προφίλ σου (μόνο αυτό αλλάζεις)
├── requirements.txt
├── setup.sh                ← macOS installer + LaunchAgent
├── dashboard.html          ← Παράγεται αυτόματα
├── data/
│   ├── seen.db             ← SQLite ιστορικό
│   └── log.txt             ← Logs
└── .github/
    └── workflows/
        └── daily.yml       ← GitHub Actions
```

---

## 📡 Πηγές που παρακολουθεί

| Κατηγορία | Sites |
|---|---|
| 🏛️ Ελληνική Κυβέρνηση | ΔΥΠΑ, gov.gr, ΟΠΕΚΑ, ΤΕΕ |
| 💶 ΕΣΠΑ | espa.gr, antagonistikotita.gr |
| 🇪🇺 Ευρωπαϊκά | EURES, EURAXESS, EU Youth Portal |
| 🇹🇷 Τουρκία | Türkiye Scholarships, TÜBİTAK |
| 💼 Εργασία | Kariera.gr, Skywalker |
| 📰 Ειδήσεις | Epixeiro, Newmoney, Opportunity Desk |

*Πρόσθεσε δικά σου sites στο `config.yaml`*

---

## 🤝 Contributing

Pull requests welcome! Ιδέες:
- Νέες πηγές (sites)
- Email notifications
- Windows/Linux LaunchAgent equivalent
- Web UI για config management

---

## 📄 License

MIT — Ελεύθερη χρήση και τροποποίηση.

---

*Built with Python 🐍 | Για την ελληνική κοινότητα ανέργων & νέων επαγγελματιών*
