from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
import shutil
from bs4 import BeautifulSoup
import markdownify
import logging
import sys

class Browser:
    def __init__(self, headless=False, anticaptcha_install=False):
        """Initialize the browser with optional headless mode."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }
        self.anticaptcha = "https://chrome.google.com/webstore/detail/nopecha-captcha-solver/dknlfmjaanfblgfdfebhijalfmhmjjjo/related"
        try:
            chrome_options = Options()
            chrome_path = Browser.get_chrome_path()
            
            if not chrome_path:
                raise FileNotFoundError("Google Chrome not found. Please install it.")
            chrome_options.binary_location = chrome_path
            
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
             # Automatically find ChromeDriver path
            chromedriver_path = shutil.which("chromedriver")
            service = Service(chromedriver_path)
            if chromedriver_path:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(service=service)
                #raise FileNotFoundError("ChromeDriver not found. Please install it or add it to your PATH.")
            self.wait = WebDriverWait(self.driver, 10)
            self.logger = logging.getLogger(__name__)
            self.logger.info("Browser initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")
            
    @staticmethod
    def get_chrome_path():
        if sys.platform.startswith("win"):
            paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe")  # User install
            ]
        elif sys.platform.startswith("darwin"):  # macOS
            paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"]
        else:  # Linux
            paths = ["/usr/bin/chromium-browser", "/usr/bin/google-chrome", "/usr/bin/chromium"]

        for path in paths:
            if os.path.exists(path) and os.access(path, os.X_OK):  # Check if executable
                return path
        return None

    
    def go_to(self, url):
        """Navigate to a specified URL."""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            self.logger.info(f"Navigated to: {url}")
            return True
        except WebDriverException as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def is_sentence(self, text):
        """Check if the text qualifies as a meaningful sentence or contains important error codes."""
        text = text.strip()
        error_codes = ["404", "403", "500", "502", "503"]
        if any(code in text for code in error_codes):
            return True
        words = text.split()
        word_count = len(words)
        has_punctuation = text.endswith(('.', '!', '?'))
        is_long_enough = word_count > 5
        has_letters = any(word.isalpha() for word in words)
        return (word_count >= 5 and (has_punctuation or is_long_enough) and has_letters)

    def get_text(self):
        """Get page text and convert it to README (Markdown) format."""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            for element in soup(['script', 'style']):
                element.decompose()
            
            text = soup.get_text()
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk and self.is_sentence(chunk))
            
            markdown_text = markdownify.markdownify(text, heading_style="ATX")
            
            return markdown_text
        except Exception as e:
            self.logger.error(f"Error getting text: {str(e)}")
            return None
    
    def clean_url(self, url):
        clean = url.split('#')[0]
        parts = clean.split('?', 1)
        base_url = parts[0]
        if len(parts) > 1:
            query = parts[1]
            essential_params = []
            for param in query.split('&'):
                if param.startswith('_skw=') or param.startswith('q=') or param.startswith('s='):
                    essential_params.append(param)
                elif param.startswith('_') or param.startswith('hash=') or param.startswith('itmmeta='):
                    break
            if essential_params:
                return f"{base_url}?{'&'.join(essential_params)}"
        return base_url

    def get_navigable(self):
        """Get all navigable links on the current page."""
        try:
            links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                href = element.get_attribute("href")
                if href and href.startswith(("http", "https")):
                    links.append({
                        "url": href,
                        "text": element.text.strip(),
                        "is_displayed": element.is_displayed()
                    })
            
            self.logger.info(f"Found {len(links)} navigable links")
            return [self.clean_url(link['url']) for link in links if link['is_displayed'] == True and len(link) < 256]
        except Exception as e:
            self.logger.error(f"Error getting navigable links: {str(e)}")
            return []

    def click_element(self, xpath):
        """Click an element specified by xpath."""
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            time.sleep(2)  # Wait for action to complete
            return True
        except TimeoutException:
            self.logger.error(f"Element not found or not clickable: {xpath}")
            return False

    def get_current_url(self):
        """Get the current URL of the page."""
        return self.driver.current_url

    def get_page_title(self):
        """Get the title of the current page."""
        return self.driver.title

    def scroll_bottom(self):
        """Scroll to the bottom of the page."""
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1)  # Wait for scroll to complete
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {str(e)}")
            return False

    def screenshot(self, filename):
        """Take a screenshot of the current page."""
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return False

    def close(self):
        """Close the browser."""
        try:
            self.driver.quit()
            self.logger.info("Browser closed")
        except Exception as e:
            raise e

    def __del__(self):
        """Destructor to ensure browser is closed."""
        self.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    browser = Browser(headless=False)
    
    try:
        browser.go_to("https://karpathy.github.io/")
        text = browser.get_text()
        print("Page Text in Markdown:")
        print(text)
        links = browser.get_navigable()
        print("\nNavigable Links:", links)
    finally:
        browser.close()
