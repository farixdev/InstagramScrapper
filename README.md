#Instagram Scraper (Google Maps Based)

This is a desktop automation project that collects Instagram-related business data using Google Maps.
The tool searches for businesses based on a given area and business domain, visits their listings, checks their websites, and extracts Instagram links if available. All collected data is saved into a CSV file.
Built to reduce manual work. That’s it.

#What It Does
Takes an area/location as input
Takes one or more business domains (restaurant, cafe, cleaner, salon, gym, etc.)

Searches Google Maps using combinations like:
restaurant near Lahore
salon near DHA Karachi

For each business found:
Collects business name
Gets Google Maps listing
Visits the business website (if available)
Extracts Instagram profile link
Saves everything into a CSV file

#How the UI Works

Enter an area
Click Edit Domain to add or remove domains (popup window)
Click Start
Wait
CSV file is generated

No login. No cloud. Runs locally.

#Installation
Requirements

Python 3.9+
Google Chrome
Internet connection

Setup
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt

How to Run
python main.py


Then use the UI.

Output

Data is saved as a CSV file.

Typical fields:

Business Name

Area

Domain

Website

Instagram URL

Google Maps Link

Tech Used

Python

Selenium

BeautifulSoup

Pandas

Desktop GUI (PyQt / Tkinter)

Notes

Scraping depends on Google Maps and website structure

Some businesses won’t have websites or Instagram

Results may vary

Disclaimer

This project is for educational and research purposes.
You are responsible for how you use it and for respecting website terms.
