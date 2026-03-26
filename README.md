# 🎯 Opportunity Hunter

> Αυτόματο σύστημα που ψάχνει καθημερινά για επιδοτήσεις, επιδόματα, θέσεις εργασίας και ευκαιρίες — και σου τα στέλνει στο Telegram κάθε πρωί.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Cloud-lightgrey)

---

## Τι κάνει

Κάθε πρωί στις 09:00, αυτόματα:

1. Ψάχνει 19+ sites (ΔΥΠΑ, ΕΣΠΑ, EURES, Türkiye Scholarships, job boards κ.α.)
2. Βρίσκει ό,τι ταιριάζει με τα keywords σου
3. Κρατάει μόνο τα ΝΕΑ — δεν επαναλαμβάνει παλιά αποτελέσματα
4. Στέλνει **Telegram μήνυμα** με τις κορυφαίες ευκαιρίες
5. Δημιουργεί **HTML Dashboard** με search και φίλτρα
6. Σου θυμίζει για **deadlines** 7, 3 και 1 μέρα πριν

---

## Οδηγός Εγκατάστασης — Βήμα Βήμα

> ✅ Κατάλληλο για αρχάριους — δεν χρειάζεσαι εμπειρία προγραμματισμού

### Μέρος 1: Κατέβασε τον κώδικα

**Βήμα 1.** Άνοιξε το Terminal:
- **macOS:** Πάτα `Cmd + Space`, γράψε `Terminal`, Enter
- **Windows:** Πάτα `Win + R`, γράψε `cmd`, Enter

**Βήμα 2.** Κατέβασε το project:
```bash
git clone https://github.com/AthanGeorgoulas/opportunity-hunter.git
cd opportunity-hunter
```

> ⚠️ Αν βγει σφάλμα "git not found": κατέβασε το Git από https://git-scm.com/downloads

---

### Μέρος 2: Εγκατάσταση Python

**macOS:**
```bash
# Άνοιξε Terminal και τρέξε:
python3 --version
```
Αν βγει `Python 3.x.x` — είσαι έτοιμος. Αλλιώς:
```bash
# Εγκατάσταση μέσω Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12
```

**Windows:**
1. Πήγαινε στο https://python.org/downloads
2. Κατέβασε Python 3.12
3. Κατά την εγκατάσταση, τσέκαρε **"Add Python to PATH"** ✅
4. Επανεκκίνηση υπολογιστή

**Βήμα 3.** Εγκατέστησε τα απαιτούμενα:
```bash
pip3 install -r requirements.txt
```

---

### Μέρος 3: Ρύθμισε το Προφίλ σου

**Βήμα 4.** Αντέγραψε το αρχείο παραδείγματος:
```bash
cp config.example.yaml config.yaml
```

**Βήμα 5.** Άνοιξε το `config.yaml` για επεξεργασία:

- **macOS:** `open -e config.yaml`
- **Windows:** `notepad config.yaml`

**Βήμα 6.** Άλλαξε τα παρακάτω σύμφωνα με εσένα:

```yaml
profile:
  name: "Το Όνομά σου"
  age: 28                      # η ηλικία σου
  status: "unemployed"         # unemployed / employed / student
  dypa_card: true              # true αν έχεις κάρτα ανεργίας ΔΥΠΑ
  income_annual: 8000          # ετήσιο εισόδημα σε ευρώ
```

**Βήμα 7.** Πρόσθεσε keywords που σε αφορούν:

```yaml
keywords_high:
  - "νοσηλευτ"       # αν είσαι νοσηλευτής
  - "λογιστ"         # αν είσαι λογιστής
  - "μηχανικ"        # αν είσαι μηχανικός
  - "voucher"        # πάντα χρήσιμο
  - "εσπα"           # πάντα χρήσιμο
  - "επιδότηση"      # πάντα χρήσιμο
```

> 💡 **Συμβουλή:** Σκέψου τι λέξεις θα έχει ο τίτλος μιας ευκαιρίας που σε αφορά και βάλε αυτές τις λέξεις ή τμήματά τους.

---

### Μέρος 4: Ρύθμιση Telegram (για ειδοποιήσεις στο κινητό)

> Αυτό είναι το πιο χρήσιμο κομμάτι — λαμβάνεις τα αποτελέσματα κατευθείαν στο κινητό σου!

**Βήμα 8.** Δημιούργησε Telegram Bot:

1. Άνοιξε Telegram στο κινητό
2. Αναζήτησε **@BotFather**
3. Γράψε: `/newbot`
4. Δώσε όνομα π.χ.: `My Opportunity Hunter`
5. Δώσε username π.χ.: `myopphunter_bot` (πρέπει να τελειώνει σε `_bot`)
6. Αντέγραψε το **token** που σου δίνει (μοιάζει με: `1234567890:AAF-xyz...`)

**Βήμα 9.** Βρες το chat ID σου:

1. Telegram → αναζήτησε **@userinfobot**
2. Γράψε `/start`
3. Αντέγραψε τον αριθμό δίπλα στο **Id:** (π.χ. `987654321`)

**Βήμα 10.** Ενεργοποίησε το bot:

1. Telegram → αναζήτησε τον bot σου (το username που έδωσες)
2. Πάτα **START**

**Βήμα 11.** Βάλε τα στοιχεία στο `config.yaml`:

```yaml
notifications:
  telegram_enabled: true
  telegram_token: "1234567890:AAF-xyz..."    # το token σου
  telegram_chat_id: "987654321"              # το chat ID σου
```

> 🔒 **ΣΗΜΑΝΤΙΚΟ:** Το `config.yaml` ΔΕΝ ανεβαίνει στο GitHub — είναι μόνο τοπικό. Μην μοιράζεσαι ποτέ το token σου.

---

### Μέρος 5: Πρώτο Test

**Βήμα 12.** Τρέξε το script:

```bash
python3 opportunity_hunter.py
```

Θα δεις στο Terminal κάτι σαν:
```
🔍 Opportunity Hunter v3.0 — 2026-03-27
  ↳ ΔΥΠΑ — Νέα …
  ↳ ΕΣΠΑ …
  ...
✅ Ολοκληρώθηκε.
```

**Βήμα 13.** Έλεγξε:
- 📱 Telegram: ήρθε μήνυμα με αποτελέσματα;
- 💻 Dashboard: `open dashboard.html` (macOS) ή διπλό κλικ στο αρχείο (Windows)

---

### Μέρος 6: Αυτόματη Εκτέλεση κάθε μέρα

**macOS — Τρέχει αυτόματα στις 09:00:**
```bash
chmod +x setup.sh && ./setup.sh
```

**Windows — Χειροκίνητο ή Task Scheduler:**

Για χειροκίνητο, τρέξε κάθε πρωί:
```bash
python opportunity_hunter.py
```

Για αυτόματο (Task Scheduler):
1. Αναζήτησε "Task Scheduler" στα Windows
2. Create Basic Task
3. Trigger: Daily, 09:00
4. Action: Start a program → `python`
5. Arguments: `C:\path\to\opportunity-hunter\opportunity_hunter.py`

---

### Μέρος 7: GitHub Actions (Τρέχει στο Cloud — Προαιρετικό)

Αν θέλεις να τρέχει ακόμα κι όταν ο υπολογιστής είναι κλειστός:

**Βήμα 14.** Κάνε Fork το repo:
- Πήγαινε στο https://github.com/AthanGeorgoulas/opportunity-hunter
- Πάτα **Fork** πάνω δεξιά

**Βήμα 15.** Πρόσθεσε τα secrets σου:
- Settings → Secrets and variables → Actions → New repository secret
- Πρόσθεσε: `TELEGRAM_TOKEN` (το token σου)
- Πρόσθεσε: `TELEGRAM_CHAT_ID` (το chat ID σου)

**Βήμα 16.** Ενεργοποίησε το workflow:
- Actions → Daily Opportunity Hunt → Enable workflow

Από εκεί τρέχει μόνο του κάθε μέρα στις 09:00 (Ελλάδα).

---

## Προσαρμογή για τον τομέα σου

### Παραδείγματα keywords ανά επάγγελμα:

```yaml
# Μηχανικός / IT:
- "τηλεπικοινωνι"
- "software"
- "network"
- "πληροφορικ"

# Νοσηλευτής / Υγεία:
- "νοσηλευτ"
- "υγει"
- "ιατρ"
- "φαρμακ"

# Λογιστής / Οικονομικά:
- "λογιστ"
- "οικονομολ"
- "χρηματοοικον"

# Δάσκαλος / Εκπαίδευση:
- "εκπαιδευτ"
- "δάσκαλ"
- "καθηγητ"
- "τεχν επαγγ εκπαιδ"

# Τουρισμός:
- "τουρισμ"
- "ξενοδοχ"
- "εστιατ"
- "tourism"
```

### Προσθήκη νέου site:

```yaml
sources:
  - name: "Όνομα Site"
    url: "https://example.com/news"
    selector: "h2 a, h3 a, article a"
    base_url: "https://example.com"
    category: "Κατηγορία"
    priority: HIGH
```

---

## Συχνές Ερωτήσεις

**Δ: Δεν βλέπω αποτελέσματα στο Telegram.**
Α: Βεβαιώσου ότι έχεις πατήσει START στον bot σου στο Telegram. Μετά τρέξε ξανά το script.

**Δ: Βγαίνει σφάλμα "ModuleNotFoundError".**
Α: Τρέξε `pip3 install -r requirements.txt` ξανά.

**Δ: Βλέπω πολλά άσχετα αποτελέσματα.**
Α: Αφαίρεσε γενικά keywords από το `config.yaml` και κράτα μόνο αυτά που αφορούν τον τομέα σου.

**Δ: Θέλω να προσθέσω αποτελέσματα από άλλη χώρα.**
Α: Πρόσθεσε το site της χώρας στη λίστα `sources` του `config.yaml`.

**Δ: Πώς σταματάω το αυτόματο τρέξιμο (macOS);**
Α:
```bash
launchctl unload ~/Library/LaunchAgents/com.thanasis.opportunityhunter.plist
```

---

## Δομή Αρχείων

```
opportunity-hunter/
├── opportunity_hunter.py   ← Κύριο script
├── config.example.yaml     ← Template — αντέγραψε σε config.yaml
├── config.yaml             ← Οι ρυθμίσεις σου (ΔΕΝ ανεβαίνει στο GitHub)
├── requirements.txt        ← Python dependencies
├── setup.sh                ← macOS scheduler
├── dashboard.html          ← Δημιουργείται αυτόματα μετά από κάθε run
├── CONTRIBUTING.md         ← Πώς να συνεισφέρεις
└── .github/workflows/
    └── daily.yml           ← GitHub Actions
```

---

## Contributing

Pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — Ελεύθερη χρήση και τροποποίηση.

---

*Φτιαγμένο με Python 🐍 | Για ανέργους, φοιτητές και νέους επαγγελματίες που ψάχνουν ευκαιρίες στην Ελλάδα και την Ευρώπη.*
