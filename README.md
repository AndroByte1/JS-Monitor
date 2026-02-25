## JS-Monitor
<sub>Track. Diff. Alert. Repeat.</sub>

A lightweight reconnaissance automation tool built for bug bounty hunters and security researchers.

It monitors JavaScript files, extracts endpoints using xnLinkFinder, compares them against historical scans, and instantly alerts you on Discord when new endpoints appear.


## Installation

To install **JS_MON**:

```bash
git clone https://github.com/AndroByte1/JS-Monitor.git
cd JS_MON
```

---

### Requirements

- Python 3.7+
- xnLinkFinder

Install dependencies:

```bash
pip install requests
pip install xnLinkFinder
```

---

### Configure Discord Webhook

Edit the script and set:

```python
DISCORD_WEBHOOK_URL = "your_webhook_here"
```

---

### Add Targets

Create a file named `urls.txt`:

```
https://target.com/app.js
https://example.com/main.js
```

---

### Run

```bash
python3 Main.py
```
