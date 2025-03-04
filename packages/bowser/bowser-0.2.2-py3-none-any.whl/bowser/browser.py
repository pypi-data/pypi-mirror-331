import time
import json
import logging
import os
import platform
import subprocess
from typing import Optional, Any, Callable, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

# Try to import UserAgent from fake_useragent.
# If that fails (e.g. due to the "type object is not subscriptable" issue), use a fallback.
try:
    from fake_useragent import UserAgent
except TypeError as e:
    logging.warning("fake_useragent import failed with error: %s. Using fallback UserAgent.", e)
    class UserAgent:
        @staticmethod
        def random() -> str:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"

# Configure logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Custom Exceptions
# ---------------------------
class BrowserSessionError(Exception):
    """Raised when the browser session is not active."""
    pass

class ElementNotFoundError(Exception):
    """Raised when a requested element cannot be found."""
    pass

# ---------------------------
# Hook Types
# ---------------------------
HookFunction = Callable[..., None]

# ---------------------------
# Helper Functions for JavaScript Injection
# ---------------------------
def get_stealth_script() -> str:
    """
    Returns a JavaScript snippet that applies stealth modifications
    to reduce Selenium detection.
    """
    return """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
    Object.defineProperty(navigator.connection, 'rtt', {get: () => 100});
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' || parameters.name === 'midi' || parameters.name === 'camera'
            ? Promise.resolve({ state: 'granted' })
            : originalQuery(parameters)
    );
    Object.defineProperty(window, 'RTCPeerConnection', {get: () => function() { return null; }});
    HTMLCanvasElement.prototype.toDataURL = (function(original) {
        return function(...args) { return original.apply(this, args); };
    })(HTMLCanvasElement.prototype.toDataURL);
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return "Intel Open Source Technology Center";
        if (parameter === 37446) return "Mesa DRI Intel(R) HD Graphics 620";
        return getParameter(parameter);
    };
    """

def get_debug_toolbar_script() -> str:
    """
    Returns a JavaScript snippet that injects a debugging toolbar into the page.
    """
    return r"""
    window.addEventListener('DOMContentLoaded', function(){
        if (!document.getElementById('selenium-toolbar-icon')) {
            var toolbarIcon = document.createElement('div');
            toolbarIcon.id = 'selenium-toolbar-icon';
            toolbarIcon.style.position = 'fixed';
            toolbarIcon.style.top = '10px';
            toolbarIcon.style.right = '10px';
            toolbarIcon.style.width = '40px';
            toolbarIcon.style.height = '40px';
            toolbarIcon.style.backgroundColor = '#333';
            toolbarIcon.style.color = '#fff';
            toolbarIcon.style.borderRadius = '5px';
            toolbarIcon.style.display = 'flex';
            toolbarIcon.style.alignItems = 'center';
            toolbarIcon.style.justifyContent = 'center';
            toolbarIcon.style.cursor = 'pointer';
            toolbarIcon.style.zIndex = '999999';
            toolbarIcon.innerText = '☰';
            document.body.appendChild(toolbarIcon);

            var toolbar = document.createElement('div');
            toolbar.id = 'selenium-toolbar';
            toolbar.style.position = 'fixed';
            toolbar.style.top = '60px';
            toolbar.style.right = '10px';
            toolbar.style.backgroundColor = '#333';
            toolbar.style.color = '#fff';
            toolbar.style.padding = '10px';
            toolbar.style.zIndex = '999999';
            toolbar.style.fontFamily = 'Arial, sans-serif';
            toolbar.style.display = 'none';
            toolbar.innerHTML = '<button id="toggle-highlight" style="cursor:pointer;">Enable Element Highlight</button>';
            document.body.appendChild(toolbar);

            toolbarIcon.addEventListener('click', function(e){
                toolbar.style.display = toolbar.style.display === 'none' ? 'block' : 'none';
            });

            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                toolbar.style.display = toolbar.style.display === 'none' ? 'block' : 'none';
            });

            var highlightMode = false;
            function getCssSelector(el) {
                if (el.id) return '#' + el.id;
                var path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    var selector = el.nodeName.toLowerCase();
                    if (el.className) {
                        var classes = el.className.trim().split(/\s+/);
                        if (classes.length) selector += '.' + classes.join('.');
                    }
                    var sibling = el;
                    var nth = 1;
                    while (sibling = sibling.previousElementSibling) {
                        if (sibling.nodeName.toLowerCase() == el.nodeName.toLowerCase()) nth++;
                    }
                    selector += ":nth-of-type(" + nth + ")";
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            }
            function mouseOverHandler(e) { e.target.style.outline = '2px solid red'; e.stopPropagation(); }
            function mouseOutHandler(e) { e.target.style.outline = ''; e.stopPropagation(); }
            function clickHandler(e) {
                e.preventDefault(); e.stopPropagation();
                var selector = getCssSelector(e.target);
                navigator.clipboard.writeText(selector).then(function() {
                    alert("Copied selector: " + selector);
                });
                disableHighlightMode();
            }
            function enableHighlightMode() {
                highlightMode = true;
                document.body.addEventListener('mouseover', mouseOverHandler, true);
                document.body.addEventListener('mouseout', mouseOutHandler, true);
                document.body.addEventListener('click', clickHandler, true);
                document.getElementById('toggle-highlight').innerText = 'Disable Element Highlight';
            }
            function disableHighlightMode() {
                highlightMode = false;
                document.body.removeEventListener('mouseover', mouseOverHandler, true);
                document.body.removeEventListener('mouseout', mouseOutHandler, true);
                document.body.removeEventListener('click', clickHandler, true);
                document.getElementById('toggle-highlight').innerText = 'Enable Element Highlight';
            }
            document.getElementById('toggle-highlight').addEventListener('click', function(e){
                e.preventDefault();
                highlightMode ? disableHighlightMode() : enableHighlightMode();
            });
        }
    });
    """

# ---------------------------
# Helper Function to Auto-Detect Chrome Binary
# ---------------------------
def _get_default_chrome_binary() -> Optional[str]:
    """
    Attempts to auto-detect the Chrome binary on the system by checking common installation paths.
    Users can override this by setting the CHROME_BIN environment variable.
    """
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        return chrome_bin

    system = platform.system().lower()
    if system == 'linux':
        for path in ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]:
            if os.path.exists(path):
                return path
    elif system == 'darwin':  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
    elif system == 'windows':
        paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    return None

# ---------------------------
# Function to Automatically Install Chrome (Linux Only)
# ---------------------------
def auto_install_chrome() -> None:
    """
    Attempts to install Google Chrome automatically on Linux systems.
    This uses apt-get and requires that the environment allows package installation.
    """
    system = platform.system().lower()
    if system != 'linux':
        raise Exception("Automatic installation of Chrome is supported only on Linux.")
    try:
        logger.info("Updating package lists...")
        subprocess.check_call(["apt-get", "update"])
        logger.info("Installing Google Chrome...")
        subprocess.check_call(["apt-get", "install", "-y", "google-chrome-stable"])
    except subprocess.CalledProcessError as e:
        logger.error("Failed to install Google Chrome: %s", e)
        raise e

# ---------------------------
# SimpleBrowser Class Definition
# ---------------------------
class browser:
    """
    A streamlined browser helper that sets up a Selenium Chrome driver with stealth
    techniques and exposes high-level methods to interact with elements—even those in
    iframes or shadow DOMs. It also supports Tor, headless mode, a debugging toolbar, and
    allows for custom hooks to extend functionality.
    
    Usage:
        with browser(website="example.com", headless=True) as browser:
            element = browser.find(selector="div.some-class")
            if element:
                browser.click(selector="div.some-class button")
            info = browser.get_info()
    """
    def __init__(self, website: str = "", wait_time: int = 10, hide_selenium: bool = True,
                 use_tor: bool = False, headless: bool = False, crash_prevention: bool = True,
                 no_sandbox: bool = False, print_extra: bool = False, add_toolbar: bool = True,
                 custom_options: Optional[Options] = None) -> None:
        self.wait_time: int = wait_time
        self.user_agent: Optional[str] = None
        self.driver: Optional[webdriver.Chrome] = None
        self.print_extra: bool = print_extra
        # Hooks for actions: keys can be 'before_click', 'after_click', 'before_fill', etc.
        self.hooks: Dict[str, HookFunction] = {}
        try:
            self.driver = self._setup(website, hide_selenium, use_tor, headless,
                                       crash_prevention, no_sandbox, add_toolbar, custom_options)
        except Exception as e:
            logger.error("Error during driver setup: %s", e)
            self.driver = None

    # ---------------------------
    # Context Manager & Lifecycle
    # ---------------------------
    def __enter__(self) -> 'browser':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.quit()

    def __del__(self) -> None:
        self.quit()

    # ---------------------------
    # Hook Registration
    # ---------------------------
    def add_hook(self, event: str, hook_fn: HookFunction) -> None:
        """
        Registers a hook function for a given event.
        For example, 'before_click' or 'after_fill'.
        """
        self.hooks[event] = hook_fn

    def _run_hook(self, event: str, *args: Any, **kwargs: Any) -> None:
        hook = self.hooks.get(event)
        if hook:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                logger.error("Error in hook '%s': %s", event, e)

    # ---------------------------
    # Driver Setup & Utility Methods
    # ---------------------------
    def _check_driver(self) -> bool:
        """Check if the driver session is still active."""
        try:
            _ = self.driver.current_url  # type: ignore
            return True
        except (WebDriverException, NoSuchWindowException):
            logger.error("Browser session is not active. It might have been closed externally.")
            raise BrowserSessionError("Browser session is inactive.")

    def _setup(self, website: str, hide_selenium: bool, use_tor: bool, headless: bool,
               crash_prevention: bool, no_sandbox: bool, add_toolbar: bool,
               custom_options: Optional[Options] = None) -> webdriver.Chrome:
        options = Options()
        service = Service(ChromeDriverManager().install())

        if no_sandbox:
            options.add_argument('--no-sandbox')
        if hide_selenium:
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument("--incognito")
            self.user_agent = UserAgent().random
            options.add_argument(f'user-agent={self.user_agent}')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
        if crash_prevention:
            options.add_argument('--disable-dev-shm-usage')
        if use_tor:
            options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        if headless:
            options.add_argument('--headless')

        # Merge in any custom options provided by the user.
        if custom_options is not None:
            for arg in custom_options.arguments:
                if arg not in options.arguments:
                    options.add_argument(arg)
            for key, value in custom_options.experimental_options.items():
                if key not in options.experimental_options:
                    options.add_experimental_option(key, value)

        # Auto-detect Chrome binary if not already set.
        if not options.binary_location:
            default_binary = _get_default_chrome_binary()
            if default_binary:
                options.binary_location = default_binary
                logger.info("Using detected Chrome binary at: %s", default_binary)
            else:
                # Attempt automatic installation on Linux.
                if platform.system().lower() == 'linux':
                    try:
                        logger.info("Chrome binary not found. Attempting to auto-install Chrome...")
                        auto_install_chrome()
                        default_binary = _get_default_chrome_binary()
                        if default_binary:
                            options.binary_location = default_binary
                            logger.info("Chrome auto-installed. Using detected Chrome binary at: %s", default_binary)
                        else:
                            logger.error("Chrome auto-install failed. Chrome binary still not found.")
                            raise WebDriverException("Chrome binary not found even after auto-install.")
                    except Exception as e:
                        logger.error("Error auto-installing Chrome: %s", e)
                        raise WebDriverException("Chrome binary not found and auto-installation failed.") from e
                else:
                    logger.error("Chrome binary not found. Ensure Chrome is installed or set CHROME_BIN.")
                    raise WebDriverException("Chrome binary not found.")

        try:
            driver = webdriver.Chrome(options=options, service=service)
        except Exception as e:
            logger.error("Error initializing Chrome WebDriver: %s", e)
            raise e

        # Apply stealth modifications.
        if hide_selenium:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": get_stealth_script()})

        # Inject debugging toolbar if desired.
        if add_toolbar:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": get_debug_toolbar_script()})

        if website:
            if not website.startswith("http"):
                website = "https://" + website
            try:
                driver.get(website)
                WebDriverWait(driver, self.wait_time).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                if self.print_extra:
                    logger.info("Navigated to %s with UserAgent: %s", website, self.user_agent)
            except WebDriverException as e:
                logger.error("Error navigating to %s: %s", website, e)
                driver.quit()
                raise e
        return driver

    def _scroll_into_view(self, element: WebElement) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -60);", element)
            WebDriverWait(self.driver, self.wait_time).until(lambda d: element.is_displayed())
        except Exception as e:
            logger.error("Error scrolling element into view: %s", e)

    # ---------------------------
    # Deep Element Searching Methods
    # ---------------------------
    def _deep_find(self, selector: str, timeout: Optional[float] = None) -> WebElement:
        """
        Deeply searches for an element matching the CSS selector through shadow DOMs and iframes.
        """
        timeout = timeout or self.wait_time
        deep_query_script = """
            function deepQuerySelector(selector) {
                function search(root) {
                    var el = root.querySelector(selector);
                    if (el) return el;
                    var children = root.querySelectorAll('*');
                    for (var i = 0; i < children.length; i++) {
                        if (children[i].shadowRoot) {
                            var shadowEl = search(children[i].shadowRoot);
                            if (shadowEl) return shadowEl;
                        }
                    }
                    var iframes = root.querySelectorAll('iframe');
                    for (var i = 0; i < iframes.length; i++) {
                        try {
                            var iframeDoc = iframes[i].contentDocument;
                            if (iframeDoc) {
                                var iframeEl = search(iframeDoc);
                                if (iframeEl) return iframeEl;
                            }
                        } catch(e) {}
                    }
                    return null;
                }
                return search(document);
            }
            return deepQuerySelector(arguments[0]);
        """
        try:
            element = WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
                lambda d: d.execute_script(deep_query_script, selector)
            )
            if element is None:
                raise ElementNotFoundError(f"Element not found with selector: {selector}")
            return element
        except TimeoutException:
            logger.error("Timeout: Element not found with selector: %s", selector)
            raise ElementNotFoundError(f"Element not found with selector: {selector}")

    def _deep_find_by_text(self, text: str, tag: str = '*', timeout: Optional[float] = None) -> WebElement:
        """
        Deeply searches for an element containing the specified text (optionally within a given tag)
        through shadow DOMs and iframes.
        """
        timeout = timeout or self.wait_time
        deep_query_by_text_script = """
            function deepQueryByText(text, tag) {
                tag = tag || '*';
                function search(root) {
                    var elements = root.getElementsByTagName(tag);
                    for (var i = 0; i < elements.length; i++) {
                        if (elements[i].textContent.includes(text)) return elements[i];
                    }
                    var all = root.querySelectorAll('*');
                    for (var i = 0; i < all.length; i++) {
                        if (all[i].shadowRoot) {
                            var shadowResult = search(all[i].shadowRoot);
                            if (shadowResult) return shadowResult;
                        }
                    }
                    var iframes = root.getElementsByTagName('iframe');
                    for (var i = 0; i < iframes.length; i++) {
                        try {
                            var iframeDoc = iframes[i].contentDocument;
                            if (iframeDoc) {
                                var iframeElements = iframeDoc.getElementsByTagName(tag);
                                for (var j = 0; j < iframeElements.length; j++) {
                                    if (iframeElements[j].textContent.includes(text)) return iframeElements[j];
                                }
                            }
                        } catch(e) {}
                    }
                    return null;
                }
                return search(document);
            }
            return deepQueryByText(arguments[0], arguments[1]);
        """
        try:
            element = WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
                lambda d: d.execute_script(deep_query_by_text_script, text, tag)
            )
            if element is None:
                raise ElementNotFoundError(f"Element with text '{text}' not found.")
            return element
        except TimeoutException:
            logger.error("Timeout: Element with text '%s' not found.", text)
            raise ElementNotFoundError(f"Element with text '{text}' not found.")

    # ---------------------------
    # High-Level Interaction Methods
    # ---------------------------
    def find(self, selector: str = "", text: Optional[str] = None, tag: str = '*') -> Optional[WebElement]:
        """
        Finds an element by either a CSS/XPath selector or (if text is provided) by its visible text.
        Deep searches through shadow DOMs and iframes are performed.
        Returns the found element or None if not found.
        """
        self._check_driver()
        try:
            if text is None:
                if selector.startswith(('/', '(', '//')):
                    element = WebDriverWait(self.driver, self.wait_time).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = self._deep_find(selector)
            else:
                element = self._deep_find_by_text(text, tag)
            self._scroll_into_view(element)
            if not element.is_enabled():
                logger.error("Element '%s' is not enabled.", selector or text)
                return None
            return element
        except Exception as e:
            logger.error("Error in find(): %s", e)
            return None

    def click(self, selector: str = "", text: Optional[str] = None, tag: str = '*') -> None:
        """
        Finds an element (by selector or text) and clicks it.
        Runs any registered hooks before and after the click.
        """
        self._check_driver()
        try:
            self._run_hook("before_click", selector, text, tag)
            element = self.find(selector, text, tag)
            if element is None:
                logger.error("click(): Element not found.")
                raise ElementNotFoundError("click(): Element not found.")
            WebDriverWait(self.driver, self.wait_time).until(
                lambda d: element.is_displayed() and element.is_enabled()
            )
            element.click()
            self._run_hook("after_click", selector, text, tag)
        except Exception as e:
            logger.error("Error in click(): %s", e)
            raise e

    def fill(self, selector: str, text_value: str, text_search: Optional[str] = None, tag: str = '*') -> None:
        """
        Finds an input field (by selector or, if text_search is provided, by text)
        and fills it with the provided text.
        Runs hooks before and after the fill action.
        """
        self._check_driver()
        try:
            self._run_hook("before_fill", selector, text_value, text_search, tag)
            element = self.find(selector, text_search, tag)
            if element is None:
                logger.error("fill(): Input field not found.")
                raise ElementNotFoundError("fill(): Input field not found.")
            element.clear()
            element.send_keys(text_value)
            self._run_hook("after_fill", selector, text_value, text_search, tag)
        except Exception as e:
            logger.error("Error in fill(): %s", e)
            raise e

    def select(self, selector: str, option_text: str, text_search: Optional[str] = None, tag: str = '*') -> None:
        """
        Finds a dropdown element (by selector or text) and selects an option by its visible text.
        """
        self._check_driver()
        try:
            element = self.find(selector, text_search, tag)
            if element is None:
                logger.error("select(): Dropdown not found.")
                raise ElementNotFoundError("select(): Dropdown not found.")
            Select(element).select_by_visible_text(option_text)
        except Exception as e:
            logger.error("Error in select(): %s", e)
            raise e

    def get_info(self, show: bool = True) -> Optional[dict]:
        """
        Navigates to ipinfo.io to retrieve IP and browser details.
        Returns a dictionary containing the information.
        """
        self._check_driver()
        try:
            self.driver.get("https://ipinfo.io/json")
            raw_data = self.driver.find_element(By.TAG_NAME, "pre").text
            data = json.loads(raw_data)
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            info = {
                "IP": data.get('ip', 'Unknown'),
                "Org": data.get('org', 'Unknown'),
                "Hostname": data.get('hostname', 'Unknown'),
                "Latitude": float(data['loc'].split(',')[0]) if 'loc' in data else None,
                "Longitude": float(data['loc'].split(',')[1]) if 'loc' in data else None,
                "City": data.get('city', 'Unknown'),
                "State": data.get('region', 'Unknown'),
                "Country": data.get('country', 'Unknown'),
                "Postal": data.get('postal', 'Unknown'),
                "Timezone": data.get('timezone', 'Unknown'),
                "User-Agent": user_agent
            }
            if show:
                for key, value in info.items():
                    logger.info("%s: %s", key, value)
            return info
        except Exception as e:
            logger.error("Error in get_info(): %s", e)
            return None

    def refresh(self) -> None:
        """
        Refreshes the current page and waits until it is fully loaded.
        """
        self._check_driver()
        try:
            self.driver.refresh()
            WebDriverWait(self.driver, self.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            logger.error("Error in refresh(): %s", e)

    def keep_awake(self, sleep_time: int = 9999999) -> None:
        """
        Keeps the browser session open for the specified amount of time
        (default is very long), then quits the driver.
        """
        self._check_driver()
        try:
            time.sleep(sleep_time)
            self.quit()
        except Exception as e:
            logger.error("Error in keep_awake(): %s", e)

    def quit(self) -> None:
        """
        Closes the browser and quits the driver.
        """
        try:
            if self.driver is not None:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            logger.error("Error during quit(): %s", e)
