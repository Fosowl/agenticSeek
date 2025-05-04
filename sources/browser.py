from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Tuple, Type, Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fake_useragent import UserAgent
from selenium_stealth import stealth
import undetected_chromedriver as uc
import chromedriver_autoinstaller
import certifi
import ssl
import time
import random
import os
import shutil
import tempfile
import markdownify
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.utility import pretty_print, animate_thinking
from sources.logger import Logger



def get_chrome_path() -> str:
    """Get the path to the Chrome executable."""
    if sys.platform.startswith("win"):
        paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google\\Chrome\\Application\\chrome.exe",
            ),  # User install
        ]
    elif sys.platform.startswith("darwin"):  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/opt/chrome/chrome",
            "/usr/local/bin/chrome",
        ]

    for path in paths:
        if os.path.exists(path) and os.access(path, os.X_OK):  # Check if executable
            return path
    print("Looking for Google Chrome in these locations failed:")
    print("\n".join(paths))
    chrome_path_env = os.environ.get("CHROME_EXECUTABLE_PATH")
    if (
        chrome_path_env
        and os.path.exists(chrome_path_env)
        and os.access(chrome_path_env, os.X_OK)
    ):
        return chrome_path_env
    path = input(
        "Google Chrome not found. Please enter the path to the Chrome executable: "
    )
    if os.path.exists(path) and os.access(path, os.X_OK):
        os.environ["CHROME_EXECUTABLE_PATH"] = path
        print(f"Chrome path saved to environment variable CHROME_EXECUTABLE_PATH")
        return path
    return None


def get_random_user_agent() -> str:
    """Get a random user agent string with associated vendor."""
    user_agents = [
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "vendor": "Google Inc.",
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "vendor": "Apple Inc.",
        },
        {
            "ua": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "vendor": "",
        },
    ]
    return random.choice(user_agents)


def create_driver(
    headless=False, stealth_mode=True, crx_path="./crx/nopecha.crx"
) -> webdriver.Chrome:
    """Create a Chrome WebDriver with specified options."""
    chrome_options = Options()
    chrome_path = get_chrome_path()

    if not chrome_path:
        raise FileNotFoundError("Google Chrome not found. Please install it.")
    chrome_options.binary_location = chrome_path

    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-webgl")
    user_data_dir = tempfile.mkdtemp()
    user_agent = get_random_user_agent()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--autoplay-policy=user-gesture-required")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f'user-agent={user_agent["ua"]}')
    resolutions = [(1920, 1080), (1366, 768), (1440, 900)]
    width, height = random.choice(resolutions)
    chrome_options.add_argument(f"--window-size={width},{height}")
    if not stealth_mode:
        # crx file can't be installed in stealth mode
        if not os.path.exists(crx_path):
            pretty_print(f"Anti-captcha CRX not found at {crx_path}.", color="failure")
        else:
            chrome_options.add_extension(crx_path)

    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if not os.path.exists(chromedriver_path):
        chromedriver_path = chromedriver_autoinstaller.install()

    if not chromedriver_path:
        raise FileNotFoundError(
            "ChromeDriver not found. Please install it or add it to your PATH."
        )

    service = Service(chromedriver_path)
    if stealth_mode:
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(service=service, options=chrome_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        chrome_version = driver.capabilities["browserVersion"]
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor=user_agent["vendor"],
            platform=(
                "Win64"
                if "Windows" in user_agent["ua"]
                else "MacIntel" if "Macintosh" in user_agent["ua"] else "Linux x86_64"
            ),
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver
    security_prefs = {
        "profile.default_content_setting_values.media_stream": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", security_prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(service=service, options=chrome_options)


class Browser:
    def __init__(self, driver, anticaptcha_manual_install=False):
        """Initialize the browser with optional AntiCaptcha installation."""
        self.js_scripts_folder = (
            "./sources/web_scripts/" if not __name__ == "__main__" else "./web_scripts/"
        )
        self.anticaptcha = "https://chrome.google.com/webstore/detail/nopecha-captcha-solver/dknlfmjaanfblgfdfebhijalfmhmjjjo/related"
        self.logger = Logger("browser.log")
        self.screenshot_folder = os.path.join(os.getcwd(), ".screenshots")
        self.tabs = []
        try:
            self.driver = driver
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")
        self.setup_tabs()
        if anticaptcha_manual_install:
            self.load_anticatpcha_manually()

    def setup_tabs(self):
        self.tabs = self.driver.window_handles
        self.driver.get("https://www.google.com")
        self.screenshot()

    def switch_control_tab(self):
        self.logger.log("Switching to control tab.")
        self.driver.switch_to.window(self.tabs[0])

    def load_anticatpcha_manually(self):
        pretty_print(
            "You might want to install the AntiCaptcha extension for captchas.",
            color="warning",
        )
        self.driver.get(self.anticaptcha)

    def go_to(self, url: str) -> bool:
        """Navigate to a specified URL."""
        time.sleep(random.uniform(0.4, 2.5))  # more human behavior
        try:
            initial_handles = self.driver.window_handles
            self.driver.get(url)
            try:
                wait = WebDriverWait(self.driver, timeout=10)
                wait.until(
                    lambda driver: (
                        not any(
                            keyword in driver.page_source.lower()
                            for keyword in ["checking your browser", "captcha"]
                        )
                    ),
                    message="stuck on 'checking browser' or verification screen",
                )
            except TimeoutException:
                self.logger.warning(
                    "Timeout while waiting for page to bypass 'checking your browser'"
                )
            self.apply_web_safety()
            self.logger.log(f"Navigated to: {url}")
            return True
        except TimeoutException as e:
            self.logger.error(f"Timeout waiting for {url} to load: {str(e)}")
            return False
        except WebDriverException as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Fatal error with go_to method on {url}:\n{str(e)}")
            raise e

    def is_sentence(self, text: str) -> bool:
        """Check if the text qualifies as a meaningful sentence or contains important error codes."""
        text = text.strip()

        if any(c.isdigit() for c in text):
            return True
        words = re.findall(r"\w+", text, re.UNICODE)
        word_count = len(words)
        has_punctuation = any(
            text.endswith(p)
            for p in [".", "，", ",", "!", "?", "。", "！", "？", "।", "۔"]
        )
        is_long_enough = word_count > 4
        return word_count >= 5 and (has_punctuation or is_long_enough)

    def get_text(self) -> str | None:
        """Get page text as formatted Markdown"""
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            for element in soup(["script", "style", "noscript", "meta", "link"]):
                element.decompose()
            markdown_converter = markdownify.MarkdownConverter(
                heading_style="ATX",
                strip=["a"],
                autolinks=False,
                bullets="•",
                strong_em_symbol="*",
                default_title=False,
            )
            markdown_text = markdown_converter.convert(str(soup.body))
            lines = []
            for line in markdown_text.splitlines():
                stripped = line.strip()
                if stripped and self.is_sentence(stripped):
                    cleaned = " ".join(stripped.split())
                    lines.append(cleaned)
            result = "[Start of page]\n\n" + "\n\n".join(lines) + "\n\n[End of page]"
            result = re.sub(r"!\[(.*?)\]\(.*?\)", r"[IMAGE: \1]", result)
            self.logger.info(f"Extracted text: {result[:100]}...")
            self.logger.info(f"Extracted text length: {len(result)}")
            return result[:8192]
        except Exception as e:
            self.logger.error(f"Error getting text: {str(e)}")
            return None

    def clean_url(self, url: str) -> str:
        """Clean URL to keep only the part needed for navigation to the page"""
        clean = url.split("#")[0]
        parts = clean.split("?", 1)
        base_url = parts[0]
        if len(parts) > 1:
            query = parts[1]
            essential_params = []
            for param in query.split("&"):
                if (
                    param.startswith("_skw=")
                    or param.startswith("q=")
                    or param.startswith("s=")
                ):
                    essential_params.append(param)
                elif (
                    param.startswith("_")
                    or param.startswith("hash=")
                    or param.startswith("itmmeta=")
                ):
                    break
            if essential_params:
                return f"{base_url}?{'&'.join(essential_params)}"
        return base_url

    def is_link_valid(self, url: str) -> bool:
        """Check if a URL is a valid link (page, not related to icon or metadata)."""
        if len(url) > 72:
            self.logger.warning(f"URL too long: {url}")
            return False
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            self.logger.warning(f"Invalid URL: {url}")
            return False
        if re.search(r"/\d+$", parsed_url.path):
            return False
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
        metadata_extensions = [".ico", ".xml", ".json", ".rss", ".atom"]
        for ext in image_extensions + metadata_extensions:
            if url.lower().endswith(ext):
                return False
        return True

    def get_navigable(self) -> List[str]:
        """Get all navigable links on the current page."""
        try:
            links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")

            for element in elements:
                href = element.get_attribute("href")
                if href and href.startswith(("http", "https")):
                    links.append(
                        {
                            "url": href,
                            "text": element.text.strip(),
                            "is_displayed": element.is_displayed(),
                        }
                    )

            self.logger.info(f"Found {len(links)} navigable links")
            return [
                self.clean_url(link["url"])
                for link in links
                if (link["is_displayed"] == True and self.is_link_valid(link["url"]))
            ]
        except Exception as e:
            self.logger.error(f"Error getting navigable links: {str(e)}")
            return []

    def click_element(self, xpath: str) -> bool:
        """Click an element specified by XPath."""
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            if not element.is_displayed():
                return False
            if not element.is_enabled():
                return False
            try:
                self.logger.error(f"Scrolling to element for click_element.")
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    element,
                )
                time.sleep(0.1)
                element.click()
                self.logger.info(f"Clicked element at {xpath}")
                return True
            except ElementClickInterceptedException as e:
                self.logger.error(f"Error click_element: {str(e)}")
                return False
        except TimeoutException:
            self.logger.warning(f"Timeout clicking element.")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error clicking element at {xpath}: {str(e)}")
            return False

    def load_js(self, file_name: str) -> str:
        """Load javascript from script folder to inject to page."""
        path = os.path.join(self.js_scripts_folder, file_name)
        self.logger.info(f"Loading js at {path}")
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError as e:
            raise Exception(f"Could not find: {path}") from e
        except Exception as e:
            raise e

    def find_all_inputs(self, timeout=3):
        """Find all inputs elements on the page."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            self.logger.error(f"Error waiting for input element: {str(e)}")
            return []
        time.sleep(0.5)
        script = self.load_js("find_inputs.js")
        input_elements = self.driver.execute_script(script)
        return input_elements

    def get_form_inputs(self) -> List[str]:
        """Extract all input from the page and return them."""
        try:
            input_elements = self.find_all_inputs()
            if not input_elements:
                self.logger.info("No input element on page.")
                return ["No input forms found on the page."]

            form_strings = []
            for element in input_elements:
                input_type = element.get("type") or "text"
                if (
                    input_type in ["hidden", "submit", "button", "image"]
                    or not element["displayed"]
                ):
                    continue
                input_name = element.get("text") or element.get("id") or input_type
                if input_type == "checkbox" or input_type == "radio":
                    try:
                        checked_status = (
                            "checked" if element.is_selected() else "unchecked"
                        )
                    except Exception as e:
                        continue
                    form_strings.append(f"[{input_name}]({checked_status})")
                else:
                    form_strings.append(f"[{input_name}](" ")")
            return form_strings

        except Exception as e:
            raise e

    def get_buttons_xpath(self) -> List[str]:
        """
        Find buttons and return their type and xpath.
        """
        buttons = self.driver.find_elements(
            By.TAG_NAME, "button"
        ) + self.driver.find_elements(By.XPATH, "//input[@type='submit']")
        result = []
        for i, button in enumerate(buttons):
            if not button.is_displayed() or not button.is_enabled():
                continue
            text = (
                (button.text or button.get_attribute("value") or "")
                .lower()
                .replace(" ", "")
            )
            xpath = f"(//button | //input[@type='submit'])[{i + 1}]"
            result.append((text, xpath))
        result.sort(key=lambda x: len(x[0]))
        return result

    def wait_for_submission_outcome(self, timeout: int = 10) -> bool:
        """
        Wait for a submission outcome (e.g., URL change or new element).
        """
        try:
            self.logger.info("Waiting for submission outcome...")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                lambda driver: driver.current_url != self.driver.current_url
                or driver.find_elements(By.XPATH, "//*[contains(text(), 'success')]")
            )
            self.logger.info("Detected submission outcome")
            return True
        except TimeoutException:
            self.logger.warning("No submission outcome detected")
            return False

    def find_and_click_btn(self, btn_type: str = "login", timeout: int = 5) -> bool:
        """Find and click a submit button matching the specified type."""
        buttons = self.get_buttons_xpath()
        if not buttons:
            self.logger.warning("No visible buttons found")
            return False

        for button_text, xpath in buttons:
            if (
                btn_type.lower() in button_text.lower()
                or btn_type.lower() in xpath.lower()
            ):
                try:
                    wait = WebDriverWait(self.driver, timeout)
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath)),
                        message=f"Button with XPath '{xpath}' not clickable within {timeout} seconds",
                    )
                    if self.click_element(xpath):
                        self.logger.info(
                            f"Clicked button '{button_text}' at XPath: {xpath}"
                        )
                        return True
                    else:
                        self.logger.warning(
                            f"Button '{button_text}' at XPath: {xpath} not clickable"
                        )
                        return False
                except TimeoutException:
                    self.logger.warning(
                        f"Timeout waiting for '{button_text}' button at XPath: {xpath}"
                    )
                    return False
                except Exception as e:
                    self.logger.error(
                        f"Error clicking button '{button_text}' at XPath: {xpath} - {str(e)}"
                    )
                    return False
        self.logger.warning(f"No button matching '{btn_type}' found")
        return False

    def tick_all_checkboxes(self) -> bool:
        """
        Find and tick all checkboxes on the page.
        Returns True if successful, False if any issues occur.
        """
        try:
            checkboxes = self.driver.find_elements(
                By.XPATH, "//input[@type='checkbox']"
            )
            if not checkboxes:
                self.logger.info("No checkboxes found on the page")
                return True

            for index, checkbox in enumerate(checkboxes, 1):
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(checkbox)
                    )
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                        checkbox,
                    )
                    if not checkbox.is_selected():
                        try:
                            checkbox.click()
                            self.logger.info(f"Ticked checkbox {index}")
                        except ElementClickInterceptedException:
                            self.driver.execute_script(
                                "arguments[0].click();", checkbox
                            )
                            self.logger.warning(f"Click checkbox {index} intercepted")
                    else:
                        self.logger.info(f"Checkbox {index} already ticked")
                except TimeoutException:
                    self.logger.warning(
                        f"Timeout waiting for checkbox {index} to be clickable"
                    )
                    continue
                except Exception as e:
                    self.logger.error(f"Error ticking checkbox {index}: {str(e)}")
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Error finding checkboxes: {str(e)}")
            return False

    def find_and_click_submission(self, timeout: int = 10) -> bool:
        possible_submissions = [
            "login",
            "submit",
            "register",
            "continue",
            "apply",
            "ok",
            "confirm",
            "proceed",
            "accept",
            "done",
            "finish",
            "start",
            "calculate",
        ]
        for submission in possible_submissions:
            if self.find_and_click_btn(submission, timeout):
                self.logger.info(f"Clicked on submission button: {submission}")
                return True
        self.logger.warning("No submission button found")
        return False

    def find_input_xpath_by_name(self, inputs, name: str) -> str | None:
        for field in inputs:
            if name in field["text"]:
                return field["xpath"]
        return None

    def fill_form_inputs(self, input_list: List[str]) -> bool:
        """Fill inputs based on a list of [name](value) strings."""
        if not isinstance(input_list, list):
            self.logger.error("input_list must be a list")
            return False
        inputs = self.find_all_inputs()
        try:
            for input_str in input_list:
                match = re.match(r"\[(.*?)\]\((.*?)\)", input_str)
                if not match:
                    self.logger.warning(f"Invalid format for input: {input_str}")
                    continue

                name, value = match.groups()
                name = name.strip()
                value = value.strip()
                xpath = self.find_input_xpath_by_name(inputs, name)
                if not xpath:
                    self.logger.warning(f"Input field '{name}' not found")
                    continue
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                except TimeoutException:
                    self.logger.error(
                        f"Timeout waiting for element '{name}' to be clickable"
                    )
                    continue
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", element
                )
                if not element.is_displayed() or not element.is_enabled():
                    self.logger.warning(
                        f"Element '{name}' is not interactable (not displayed or disabled)"
                    )
                    continue
                input_type = (element.get_attribute("type") or "text").lower()
                if input_type in ["checkbox", "radio"]:
                    is_checked = element.is_selected()
                    should_be_checked = value.lower() == "checked"

                    if is_checked != should_be_checked:
                        element.click()
                        self.logger.info(f"Set {name} to {value}")
                else:
                    element.clear()
                    element.send_keys(value)
                    self.logger.info(f"Filled {name} with {value}")
            return True
        except Exception as e:
            self.logger.error(f"Error filling form inputs: {str(e)}")
            return False

    def fill_form(self, input_list: List[str]) -> bool:
        """Fill form inputs based on a list of [name](value) and submit."""
        if not isinstance(input_list, list):
            self.logger.error("input_list must be a list")
            return False
        if self.fill_form_inputs(input_list):
            self.logger.info("Form filled successfully")
            self.tick_all_checkboxes()
            if self.find_and_click_submission():
                if self.wait_for_submission_outcome():
                    self.logger.info("Submission outcome detected")
                    return True
                else:
                    self.logger.warning("No submission outcome detected")
            else:
                self.logger.warning("Failed to submit form")
        self.logger.warning("Failed to fill form inputs")
        return False

    def get_current_url(self) -> str:
        """Get the current URL of the page."""
        return self.driver.current_url

    def get_page_title(self) -> str:
        """Get the title of the current page."""
        return self.driver.title

    def scroll_bottom(self) -> bool:
        """Scroll to the bottom of the page."""
        try:
            self.logger.info("Scrolling to the bottom of the page...")
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(0.5)
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {str(e)}")
            return False

    def get_screenshot(self) -> str:
        return self.screenshot_folder + "/updated_screen.png"

    def screenshot(self, filename: str = "updated_screen.png") -> bool:
        """Take a screenshot of the current page."""
        self.logger.info("Taking screenshot...")
        time.sleep(0.1)
        try:
            path = os.path.join(self.screenshot_folder, filename)
            if not os.path.exists(self.screenshot_folder):
                os.makedirs(self.screenshot_folder)
            self.driver.save_screenshot(path)
            self.logger.info(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return False

    def apply_web_safety(self):
        """
        Apply security measures to block any website malicious/annoying execution, privacy violation etc..
        """
        self.logger.info("Applying web safety measures...")
        script = self.load_js("inject_safety_script.js")
        input_elements = self.driver.execute_script(script)


if __name__ == "__main__":
    driver = create_driver(headless=False, stealth_mode=True)
    browser = Browser(driver, anticaptcha_manual_install=True)

    input("press enter to continue")
    print("AntiCaptcha / Form Test")
    # browser.go_to("https://www.browserscan.net/bot-detection")
    # txt = browser.get_text()
    # browser.go_to("https://www.google.com/recaptcha/api2/demo")
    browser.go_to("https://home.openweathermap.org/users/sign_up")
    inputs_visible = browser.get_form_inputs()
    print("inputs:", inputs_visible)
    # inputs_fill = ['[q](checked)', '[q](checked)', '[user[username]](mlg)', '[user[email]](mlg.fcu@gmail.com)', '[user[password]](placeholder_P@ssw0rd123)', '[user[password_confirmation]](placeholder_P@ssw0rd123)']
    # browser.fill_form(inputs_fill)
    input("press enter to exit")
