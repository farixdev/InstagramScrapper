<div align="center">

# 📍 Instagram Scraper via Google Maps

**A desktop automation tool that finds local businesses on Google Maps and extracts their Instagram presence — exported clean into CSV.**

![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/automation-Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

</div>

---

## 📖 Overview

This tool automates the process of finding local businesses through Google Maps and extracting their Instagram profile links. Simply enter a location and your target business categories — the tool handles the rest and delivers structured data in a ready-to-use CSV file.

---

## ✨ Features

- 🗺️ Searches Google Maps automatically based on your input
- 🏪 Supports multiple business categories (domains) in one run
- 🔗 Extracts Instagram profile links from business websites
- 📊 Exports all results to a clean CSV file
- 🖥️ Simple graphical interface — no terminal needed after launch

---

## ⚙️ How It Works

```
User Input (Area + Domains)
        ↓
Search Queries Generated
  e.g. "restaurant near Lahore"
        ↓
Google Maps Searched for Each Query
        ↓
For Each Business Found:
  ├─ Business name collected
  ├─ Google Maps listing saved
  ├─ Website visited (if available)
  └─ Instagram profile link extracted
        ↓
All Data Exported → output/results.csv
```

### Example Queries Generated

| Area | Domain | Query Sent to Google Maps |
|------|--------|--------------------------|
| Lahore | restaurant | `restaurant near Lahore` |
| DHA Karachi | salon | `salon near DHA Karachi` |
| Islamabad | gym | `gym near Islamabad` |

---

## 🖥️ User Interface

The app uses a simple GUI — no command-line interaction required after launch.

1. Enter your **target area** (city, region, or neighborhood)
2. Click **Edit Domains** to add or remove business categories
3. Click **Start** to begin scraping
4. Wait for the process to complete
5. Find your **CSV file** auto-generated in the `output/` folder

**Supported domain examples:** `restaurant`, `cafe`, `salon`, `gym`, `cleaner`, `pharmacy`, and more.

---

## 🚀 Installation

### Prerequisites

- Python `3.9` or higher
- Google Chrome (latest version)
- Active internet connection

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git

# 2. Navigate into the project
cd your-repo-name

# 3. Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

The graphical interface will launch automatically.

---

## 📁 Project Structure

```
your-repo-name/
├── output/                 # Generated CSV files saved here
├── main.py                 # Entry point & GUI
├── scraper.py              # Core scraping logic
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 📋 Output Format

Results are saved as a `.csv` file with the following columns:

| Column | Description |
|--------|-------------|
| `Business Name` | Name of the business |
| `Google Maps URL` | Direct link to the Maps listing |
| `Website` | Business website (if available) |
| `Instagram` | Extracted Instagram profile link |

---

## ⚠️ Notes & Limitations

- Some businesses may not have a website or Instagram profile — those fields will be left blank
- Results depend on Google Maps data availability and website structure
- Scraping speed may vary based on internet connection and page load times
- Use responsibly and in accordance with Google Maps' Terms of Service

---

## 👤 Author

Made with 🖤 by **[Farisxdev](https://github.com/farisxdev)**

---

<div align="center">

Found this useful? Drop a ⭐ on GitHub — it helps a lot!

</div>
