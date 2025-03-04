# Bowser Help Guide

## Overview
Bowser is a Python package built on top of Selenium for automated browser interactions. It provides a high-level API for launching Chrome, interacting with elements, and executing common browser tasks with stealth techniques.

### Installation
```sh
pip install bowser
```
or for development:
```sh
pip install -e .
```

---

## Class: `browser`
Initializes a browser session with configurable options.

### Arguments:
- `website` (str, optional) - The URL to open upon launching the browser.
- `wait_time` (int, default=`10`) - The default timeout in seconds for waiting for elements.
- `hide_selenium` (bool, default=`True`) - If `True`, applies stealth modifications to evade detection.
- `use_tor` (bool, default=`False`) - If `True`, routes traffic through Tor for anonymity.
- `headless` (bool, default=`False`) - If `True`, runs Chrome in headless mode (without UI).
- `crash_prevention` (bool, default=`True`) - If `True`, adds arguments to prevent Chrome crashes.
- `no_sandbox` (bool, default=`False`) - If `True`, enables the `--no-sandbox` argument.
- `print_extra` (bool, default=`False`) - If `True`, enables additional debugging print statements.
- `add_toolbar` (bool, default=`True`) - If `True`, injects a debugging toolbar for inspecting elements.
- `custom_options` (`selenium.webdriver.chrome.options.Options`, optional) - Allows users to provide custom Chrome options.

### Example:
```python
with browser(website="https://example.com", headless=True) as b:
    b.click(text="Get Started")
```

---

## Method: `find`
Finds an element based on a CSS selector, visible text, or tag name.

### Arguments:
- `selector` (str, default=`""`) - A CSS or XPath selector for locating the element.
- `text` (str, optional) - Searches for an element containing the specified visible text.
- `tag` (str, default=`"*"`) - Filters elements by tag name (e.g., `"button"`, `"div"`).

### Returns:
- `WebElement` if found, otherwise `None`.

### Example:
```python
element = b.find(selector="h1")
if element:
    print(element.text)
```

---

## Method: `click`
Finds an element and clicks it.

### Arguments:
- `selector` (str, default=`""`) - A CSS or XPath selector for locating the element.
- `text` (str, optional) - Clicks an element containing the specified visible text.
- `tag` (str, default=`"*"`) - Filters elements by tag name.

### Example:
```python
b.click(selector="button#submit")
b.click(text="Sign In")
```

---

## Method: `fill`
Finds an input field and enters text.

### Arguments:
- `selector` (str) - A CSS or XPath selector for locating the input field.
- `text_value` (str) - The text to enter into the field.
- `text_search` (str, optional) - If provided, finds a field near the specified text.
- `tag` (str, default=`"*"`) - Filters elements by tag name.

### Example:
```python
b.fill(selector="input[name='q']", text_value="Python automation")
```

---

## Method: `select`
Finds a dropdown and selects an option by visible text.

### Arguments:
- `selector` (str) - A CSS or XPath selector for locating the dropdown.
- `option_text` (str) - The visible text of the option to select.
- `text_search` (str, optional) - Finds a dropdown near the specified text.
- `tag` (str, default=`"*"`) - Filters elements by tag name.

### Example:
```python
b.select(selector="select#country", option_text="United States")
```

---

## Method: `get_info`
Gets browser and IP details using `ipinfo.io`.

### Arguments:
- `show` (bool, default=`True`) - If `True`, prints the retrieved information.

### Returns:
- Dictionary containing browser and IP info.

### Example:
```python
info = b.get_info()
print(info)
```

---

## Method: `refresh`
Reloads the current page.

### Arguments:
- None.

### Example:
```python
b.refresh()
```

---

## Method: `keep_awake`
Keeps the browser open for a specified duration before quitting.

### Arguments:
- `sleep_time` (int, default=`9999999`) - Time in seconds to keep the browser open.

### Example:
```python
b.keep_awake(sleep_time=60)
```

---

## Method: `quit`
Closes the browser session and cleans up resources.

### Arguments:
- None.

### Example:
```python
b.quit()
```

---

## Method: `add_hook`
Registers a function to execute before or after specific actions.

### Arguments:
- `event` (str) - The event name (e.g., `"before_click"`, `"after_fill"`).
- `hook_fn` (callable) - The function to execute when the event occurs.

### Example:
```python
def log_action():
    print("An action was performed.")

b.add_hook(event="before_click", hook_fn=log_action)
```

---

## Troubleshooting:

### 1. **ModuleNotFoundError: No module named 'bowser'**
- Ensure you're using the correct Python environment and have installed Bowser properly.
- Run: 
```sh
pip install bowser
```

### 2. **Chrome Binary Not Found**
- Set the `CHROME_BIN` environment variable or install Chrome manually.

### 3. **Browser Crashes on Start**
- Enable the crash prevention option: 
```python
browser(crash_prevention=True)
```

### 4. **Permissions Issues on Linux**
- Run Bowser with appropriate privileges or manually install Chrome.
