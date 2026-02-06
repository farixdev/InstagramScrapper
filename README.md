# Instagram Scraper using Google Maps

This project is a **desktop automation tool** that collects **Instagram-related business data** using **Google Maps**.  
The goal of the tool is to help users find local businesses in a specific area and extract their online presence in a **structured CSV format**.

---

## What This Project Does

The application allows the user to enter an **area or location**, such as a city, region, or neighborhood.  
The user can also add one or multiple **business domains**, for example:

- restaurant  
- cafe  
- cleaner  
- salon  
- gym  

Domains can be managed through a **popup window** inside the application.

---

## How It Works

1. The user enters an **area**
2. The user adds one or more **domains**
3. The program combines them into search queries like:
   - restaurant near Lahore
   - salon near DHA Karachi
4. These queries are searched on **Google Maps**
5. For each business found:
   - Business name is collected
   - Google Maps listing is saved
   - Website is visited (if available)
   - Instagram profile link is extracted
6. All data is saved into a **CSV file** in Output Folder

---

## User Interface Flow

- Enter **Area**
- Click **Edit Domain** to add or remove domains
- Click **Start**
- Wait for the process to finish
- CSV file is generated automatically

---

## Installation

### Requirements

- Python 3.9 or higher
- Google Chrome
- Internet connection

### Setup

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt 
```




# How to Run

```bash
python main.py 
```


After running the command, use the graphical interface to start scraping.


### Notes

Some businesses may not have websites or Instagram profiles Results depend on Google Maps data and website structure Scraping speed and results may vary
