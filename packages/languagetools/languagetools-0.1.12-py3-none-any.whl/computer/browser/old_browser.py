import threading
import time
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
import urllib.parse
import html2text
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import urllib
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Browser:
    def __init__(self, computer):
        self.computer = computer
        self._driver = None
        self.max_retries = 3
        self.retry_delay = 2
        self.accessibility_tree = None

    @property
    def driver(self):
        if self._driver is None:
            self.setup()
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value

    def setup(self):
        """Set up the Chrome WebDriver with retries and error handling."""
        print("Starting browser...")
        for attempt in range(self.max_retries):
            try:
                self.options = webdriver.ChromeOptions()
                # self.options.add_argument("--no-sandbox")
                # self.options.add_argument("--disable-dev-shm-usage")
                # self.options.add_argument("--disable-gpu")
                # self.options.add_argument("--window-size=1920,1080")
                # self.options.add_argument("--remote-debugging-port=9222")
                
                # Uncomment the line below if you want to run Chrome in headless mode
                # self.options.add_argument("--headless")

                self._driver = webdriver.Chrome(options=self.options)
                self._driver.set_page_load_timeout(30)  # Set page load timeout to 30 seconds
                return
            except (WebDriverException, SessionNotCreatedException) as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Unable to set up WebDriver.")
                    raise

    def search(self, query):
        """
        Searches the web for the specified query and returns the results.
        """
        headers = {"Authorization": f"Bearer {self.computer.api_key}"}
        response = requests.post(
            f'{self.computer.api_base}/tools/',
            json={"tool": "search", "input": {"query": query}},
            headers=headers
        )
        return response.json()["output"]

    def fast_search(self, query):
        return self.search(query)

    def search_google(self, query):
        """Perform a search"""

        # Perplexity
        # self.driver.get("https://www.perplexity.ai")
        # body = self.driver.find_element(By.TAG_NAME, "body")
        # body.send_keys(Keys.COMMAND + "k")
        # time.sleep(0.5)
        # active_element = self.driver.switch_to.active_element
        # active_element.send_keys(query)
        # active_element.send_keys(Keys.RETURN)
        # time.sleep(3)

        # Google

        # Use search box
        # self.driver.get("https://www.google.com")
        # search_box = self.driver.find_element(By.NAME, 'q')
        # search_box.send_keys(query)
        # search_box.send_keys(Keys.RETURN)

        # Go direct
        encoded_query = urllib.parse.quote(query)
        self.driver.get(f"https://www.google.com/search?q={encoded_query}")

        # Wait for the page to finish loading
        WebDriverWait(self.driver, 3).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

        print(self.read())
        
        # self.extract_page_info("Tell me what links I should click to answer this query, or try to answer the query if its answer is on the page: " + query)

    def extract_page_info(self, query):
        """Depracated. Extract HTML, list interactive elements, and analyze with AI"""
        html_content = self.driver.page_source
        text_content = html2text.html2text(html_content)

        # text_content = text_content[:len(text_content)//2]

        elements = (
            self.driver.find_elements(By.TAG_NAME, "a")
            + self.driver.find_elements(By.TAG_NAME, "button")
            + self.driver.find_elements(By.TAG_NAME, "input")
            + self.driver.find_elements(By.TAG_NAME, "select")
        )

        elements_info = [
            {
                "id": idx,
                "text": elem.text,
                "attributes": elem.get_attribute("outerHTML"),
            }
            for idx, elem in enumerate(elements)
        ]

        ai_query = f"""
        Below is the content of the current webpage along with interactive elements. 
        Given the query "{query}", please extract useful information and provide sufficient details 
        about interactive elements, focusing especially on those pertinent to the provided intent.
        
        If the information requested by the query "{query}" is present on the page, simply return that.

        If not, return the top 10 most relevant interactive elements in a concise, actionable format, listing them on separate lines
        with their ID, a description, and their possible action.

        Do not hallucinate.

        Page Content:
        {text_content}
        
        Interactive Elements:
        {elements_info}
        """

        response = self.computer.ai.chat(ai_query, model_size="tiny")

        print(response)
        print(
            "Please utilize this information or interact with the interactive elements provided to answer the user's query."
        )

    def get_accessibility_tree(self):
        self.driver.execute_cdp_cmd('Accessibility.enable', {})
        result = self.driver.execute_cdp_cmd('Accessibility.getFullAXTree', {})
        self.accessibility_tree = result['nodes']
        self.driver.execute_cdp_cmd('Accessibility.disable', {})
        return self.accessibility_tree

    def find_and_modify_element(self, node):
        script = """
        function findElement(role, name) {
            const elements = document.querySelectorAll(`${role}, [role="${role}"]`);
            return Array.from(elements).find(el => 
                el.textContent.trim() === name || 
                el.getAttribute('aria-label') === name ||
                el.getAttribute('alt') === name
            );
        }
        const element = findElement(arguments[0], arguments[1]);
        if (element) {
            element.setAttribute('data-ai-id', arguments[2]);
            return true;
        }
        return false;
        """
        return self.driver.execute_script(script, node['role']['value'], node['name']['value'], f"elem_{node['nodeId']}")

    def process_node(self, node, processed_nodes):

        node_id = node['nodeId']
        if node_id in processed_nodes:
            return ""

        processed_nodes.add(node_id)
        
        result = ""
        name = node.get('name', {}).get('value', '')
        role = node.get('role', {}).get('value', '')

        if role in ['StaticText', 'text']:
            result += f"{name} "
        elif role in ['link', 'button', 'textbox', 'img']:
            self.element_index += 1
            if role == 'textbox':
                result += f"[ELEMENT {self.element_index}] Input field: {name}\n"
            elif role == 'img':
                result += f"[ELEMENT {self.element_index}] Image: {name}\n"
            else:
                result += f"[ELEMENT {self.element_index}] {role.capitalize()}: {name}\n"
            
        for child in node.get('childIds', []):
            child_node = next((n for n in self.accessibility_tree if n['nodeId'] == child), None)
            if child_node:
                result += self.process_node(child_node, processed_nodes)

        return result

    def read(self, page=1):
        """
        Extracts and prints a simplified version of the webpage content based on the Chrome accessibility tree.
        Interactive elements are given unique IDs that can be used with Selenium.

        Args:
            page (int): The page number to display based on pagination.
        """
        self.get_accessibility_tree()

        root_node = next(node for node in self.accessibility_tree if node.get('role', {}).get('value') == 'RootWebArea')
        processed_nodes = set()
        self.element_index = 0
        full_content = self.process_node(root_node, processed_nodes)

        # Pagination settings
        items_per_page = 5000
        total_pages = (len(full_content) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_content = full_content[start_idx:end_idx]

        print(page_content)
        print(f"\nPage {page} of {total_pages}")
        if page < total_pages:
            print("Run browser.read(page=X) with a higher page number to see the rest.")

        print("\nTo interact with elements, use Selenium commands like:")
        print("element = driver.find_element(By.CSS_SELECTOR, '[data-ai-id=\"elem_X\"]')")
        print("element.click()  # or .send_keys('text') for inputs, etc.")

    def quit(self):
        """Close the browser"""
        self.driver.quit()

#!/usr/bin/env python3
#
# browser.py
#
# A programmatic browser automation tool using Playwright.
#
