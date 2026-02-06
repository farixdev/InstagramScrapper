import os
import sys
import re
import time
import csv
import pandas as pd
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt5.QtGui import QIcon
from urllib.parse import urlparse
from datetime import datetime


def app_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # EXE location
    return os.path.dirname(os.path.abspath(__file__))  # script location


BASE_DIR = app_base_path()
CONFIG_DIR = os.path.join(BASE_DIR, "config")

os.makedirs(CONFIG_DIR, exist_ok=True)

DOMAINS_FILE = os.path.join(CONFIG_DIR, "Domains.txt")


class ScraperWorker(QThread):
    log_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, area):
        super().__init__()
        self.area = area
        self._abort = False

    def stop(self):
        self._abort = True

    def log(self, message):
        self.log_signal.emit(message)

    
    

    def run(self):
        try:
            with open(DOMAINS_FILE, 'r', encoding='utf-8') as f:
                Domains = [line.strip() for line in f if line.strip()]

            self.log(f"Loaded {len(Domains)} domains from file")

            area_folder = os.path.join("output", self.area.replace(" ", "_"))
            os.makedirs(area_folder, exist_ok=True)

            self.log(f"Output folder ready: {area_folder}")

            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(service=Service(), options=options)
            self.log("Browser launched successfully")
            driver.set_page_load_timeout(10)
            self.log("Page load timeout set to 10 seconds")
            original_window = driver.current_window_handle

            for domain in Domains:
                self.log(f"Processing domain: {domain}")
                if self._abort:
                    break

                search_query = f"{domain} near {self.area}"
                fileCSV = os.path.join(area_folder, f"{domain}.csv")
                self.log(f"Searching: {search_query}")

                try:
                    self.log("Opening Google Maps")
                    driver.get("https://www.google.com/maps")

                    wait = WebDriverWait(driver, 20)

                    # Handle consent if it appears
                    try:
                        agree = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//button//span[text()="Accept all"]')
                        ))
                        agree.click()
                        self.log("Consent accepted")
                    except:
                        pass  # No consent shown

                    # Now wait for search box
                    search_box = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'input[name="q"]')
                    ))
                    self.log("Search box ready")

                    time.sleep(1.5)  # 👈 let Maps JS settle

                    search_box.clear()
                    search_box.send_keys(search_query)
                    time.sleep(0.3)
                    search_box.send_keys(Keys.ENTER)
                    self.log("Search submitted")
                    wait.until(
                            lambda d: (
                                "/search/" in d.current_url or
                                len(d.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')) > 0
                            )

                            
                        )
                    
                    self.log("Search results detected")
                except Exception as e:
                    self.log(f"Failed to search: {e}")
                    continue

                try:
                    feed = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                    )
                    self.log("Results feed located")
                except:
                    self.log("⚠️ Results feed not found. Skipping scrolling.")
                    feed = None


                
                if feed:

                    last_count = 0
                    stable_rounds = 0
        
                    while not self._abort:
                        driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight",
                            feed
                        )
                        time.sleep(2)

                        cards = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
                        current_count = len(cards)
                        self.log(f"Loaded {current_count} results…")

                        if current_count == last_count:
                            stable_rounds += 1
                        else:
                            stable_rounds = 0

                        if stable_rounds >= 2:
                            break

                        last_count = current_count

                    business_cards = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
                    self.log(f"Found {len(business_cards)} businesses for: {domain}")
                    self.log(f"Creating CSV file: {fileCSV}")
                    with open(fileCSV, "w", newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Business Index", "Business Name", "Website URL"])

                        processed = set()
                        index = 0

                        while index < len(business_cards):
                            if self._abort:
                                break
                            try:
                                business_cards = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
                                if index >= len(business_cards):
                                    break
                                card = business_cards[index]
                                business_name = card.get_attribute("aria-label")
                                business_link = card.get_attribute("href")

                                if not business_link or business_link in processed:
                                    index += 1
                                    continue

                                processed.add(business_link)
                                self.log(f"Opening business page: {business_name}")
                                driver.execute_script("window.open(arguments[0]);", business_link)
                                time.sleep(2)
                                driver.switch_to.window(driver.window_handles[-1])
                                self.log("Business page loaded")
                                time.sleep(5)

                                try:
                                    website_button = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]')
                                    website_url = website_button.get_attribute("href")
                                    self.log(f"[{index + 1}] {business_name} -> {website_url}")
                                    writer.writerow([index + 1, business_name, website_url])
                                except:
                                    self.log(f"[{index + 1}] {business_name} -> No website found")
                                self.log("Closing business tab")
                                driver.close()
                                driver.switch_to.window(original_window)
                                index += 1
                            except Exception as e:
                                self.log(f"⚠️ Error at business #{index + 1}: {e}")
                                for handle in driver.window_handles:
                                    if handle != original_window:
                                        driver.switch_to.window(handle)
                                        driver.close()
                                driver.switch_to.window(original_window)
                                index += 1

                try:
                    df = pd.read_csv(fileCSV)

                    def get_homepage( url):
                            try:
                                if not url.startswith("http"):
                                    url = "https://" + url
                                parsed = urlparse(url)
                                return f"{parsed.scheme}://{parsed.netloc}/"
                            except:
                                return url
                        

                    df["Instagram"] = ""
                    self.log("Starting Instagram scan for collected websites")
                    for i, row in df.iterrows():
                        url = row["Website URL"]
                        if not isinstance(url, str) or not url.startswith("http"):
                            continue
                        try:
                            
                            homepage = get_homepage(url)
                            self.log(f"Visiting homepage: {homepage}")

                            driver.get(homepage)
                            insta = ""

                            # Quick check immediately
                            page_source = driver.page_source.lower()
                            if "instagram.com" in page_source:
                                soup = BeautifulSoup(driver.page_source, "html.parser")
                                link = soup.find("a", href=re.compile(r"instagram\.com", re.I))
                                if link:
                                    insta = link["href"]
                                    self.log(f"Instagram found for {row['Business Name']}: {insta}")
                                    df.at[i, "Instagram"] = insta
                                    continue

                            if not insta:
                                self.log(f"⚠️ No Instagram found for {row['Business Name']}")

                            # Wait only if not found
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )

                            page_source = driver.page_source.lower()


                            # Skip if error detected
                            error_phrases = [
                                "something went wrong",
                                "site can’t be reached",
                                "site can't be reached",
                                "not found",
                                "access denied",
                                "error 404",
                                "403 forbidden"
                            ]

                            if any(err in page_source for err in error_phrases):
                                self.log(f"⚠️ Skipped (error page): {row['Business Name']}")
                                df.at[i, "Instagram"] = "ERROR"
                                continue

                            soup = BeautifulSoup(driver.page_source, "html.parser")
                            insta = ""
                            link = soup.find("a", href=re.compile(r"instagram\.com", re.I))
                            if link:
                                insta = link["href"]
                                self.log(f"Instagram found for {row['Business Name']}: {insta}")


                            df.at[i, "Instagram"] = insta
                        except Exception as e:
                            df.at[i, "Instagram"] = "ERROR"
                    df.to_csv(fileCSV, index=False)
                    self.log(f"Saved: {fileCSV}")
                except Exception as e:
                    self.log(f"❌ Error updating Instagram: {e}")
                
                self.log(f"Finished processing domain: {domain}")

                
            
            driver.quit()
        except Exception as e:
            self.log(f"❌ Critical error: {e}")
        self.finished.emit()

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(800, 200, 600, 400)
        self.setWindowTitle("Instagram Scraper")
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.label = QLabel("Enter Area:", self)
        self.label.move(40, 40)

        self.area_input = QLineEdit(self)
        self.area_input.setGeometry(150, 35, 300, 30)

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(150, 80, 100, 40)
        self.start_button.clicked.connect(self.toggle_scraping)

        self.edit_domains_button = QPushButton("Edit Domains", self)
        self.edit_domains_button.setGeometry(270, 80, 130, 40)
        self.edit_domains_button.clicked.connect(self.open_domain_editor)

        self.log_output = QTextEdit(self)
        self.log_output.setGeometry(40, 140, 520, 230)
        self.log_output.setReadOnly(True)

        self.setStyleSheet("""
    QMainWindow {
        background-color: #121212;
        color: #ffffff;
        font-family: 'Segoe UI';
        font-size: 14px;
    }
    QLabel {
        color: #ffffff;
    }
    QLineEdit {
        background-color: #1e1e1e;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        color: #ffffff;
        padding: 6px;
    }
    QTextEdit {
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #e5e7eb;
    font-family: Consolas, monospace;
    font-size: 13px;
    padding: 8px;
}
    QPushButton {
        background-color: #007acc;
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #005fa3;
    }
    QPushButton:pressed {
        background-color: #004b82;
    }
    QPushButton:disabled {
        background-color: #3a3a3a;
        color: #888888;
        border: 1px solid #555;
    }

    QScrollBar:vertical {
        border: none;
        background-color: #1e1e1e;
        width: 12px;
        margin: 0px 0px 0px 0px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #3a3a3a;
        min-height: 20px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #555555;
    }

    QScrollBar::sub-line:vertical,
    QScrollBar::add-line:vertical {
        height: 0px;
        subcontrol-origin: margin;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }

    QScrollBar:horizontal {
        border: none;
        background-color: #1e1e1e;
        height: 12px;
        margin: 0px 0px 0px 0px;
        border-radius: 6px;
    }

    QScrollBar::handle:horizontal {
        background-color: #3a3a3a;
        min-width: 20px;
        border-radius: 6px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #555555;
    }

    QScrollBar::sub-line:horizontal,
    QScrollBar::add-line:horizontal {
        width: 0px;
        subcontrol-origin: margin;
    }

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }
""")


    def toggle_scraping(self):
        if self.worker and self.worker.isRunning():
            self.start_button.setText("Stopping...")
            self.worker.stop()
            return

        area = self.area_input.text().strip()
        if not area:
            QMessageBox.warning(self, "Missing Area", "Please enter an area to scrape.")
            return

        self.log_output.clear()
        self.worker = ScraperWorker(area)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        self.start_button.setText("Stop")

    def open_domain_editor(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Domains")
        dialog.setGeometry(850, 300, 400, 400)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        if os.path.exists(DOMAINS_FILE):
            with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                text_edit.setText(f.read())

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(text_edit)
        layout.addLayout(btn_layout)

        def save_domains():
            try:
                with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
                    f.write(text_edit.toPlainText())
                dialog.accept()
                QMessageBox.information(self, "Saved", "Domains updated successfully.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save domains:\n{str(e)}")

        save_btn.clicked.connect(save_domains)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()

    def append_log(self, text):
    

        # timestamp
        time_str = datetime.now().strftime("%H:%M:%S")

        # detect log type
        color = "#00ffcc"   # default
        if "error" in text.lower() or "❌" in text:
            color = "#ff4d4d"  # red
        elif "skipped" in text.lower() or "⚠️" in text:
            color = "#ffaa00"  # orange
        elif "found" in text.lower():
            color = "#66ff66"  # green
        elif "searching" in text.lower():
            color = "#66aaff"  # blue

        # clickable links
        url_pattern = r"(https?://[^\s]+)"
        text = re.sub(url_pattern, r'<a href="\1" style="color:#00aaff;">\1</a>', text)

        # formatted log line
        html = f"""
        <div style="margin-bottom:6px;">
            <span style="color:#888;">[{time_str}]</span>
            <span style="color:{color};">{text}</span>
        </div><br>
        """

        self.log_output.insertHtml(html)
        self.log_output.moveCursor(QTextCursor.End)


    def on_finished(self):
        self.start_button.setText("Start")
        QMessageBox.information(self, "Done", "Scraping completed.")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    gui.show()
    sys.exit(app.exec_())
